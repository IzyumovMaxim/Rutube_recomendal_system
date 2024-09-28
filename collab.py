import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def collab(df, df1, N):
    logs = df1
    video_stats = df

    # Step 2: Data Cleaning and Preparation
    logs_clean = logs[['user_id', 'watchtime', 'video_id']]
    video_stats_clean = video_stats[['video_id', 'category_id', 'author_id']]

    merged_data = logs_clean.merge(video_stats_clean, on='video_id')

    # Step 3: Create User-Video, User-Category, and User-Author Matrices
    user_video_matrix = merged_data.pivot_table(index='user_id', columns='video_id', values='watchtime', fill_value=0)
    user_category_matrix = pd.get_dummies(merged_data[['user_id', 'category_id']].set_index('user_id')['category_id'])
    user_author_matrix = pd.get_dummies(merged_data[['user_id', 'author_id']].set_index('user_id')['author_id'])

    # Step 4: Compute User Similarities Based on Watchtime, Categories, and Authors
    user_similarity_watchtime = cosine_similarity(user_video_matrix)
    user_similarity_category = cosine_similarity(user_category_matrix)
    user_similarity_author = cosine_similarity(user_author_matrix)

    # Step 5: Combine User Similarities Using Weights
    combined_user_similarity = (
        0.5 * user_similarity_watchtime +
        0.25 * user_similarity_category +
        0.25 * user_similarity_author
    )
    combined_user_similarity_df = pd.DataFrame(combined_user_similarity, 
                                            index=user_video_matrix.index, 
                                            columns=user_video_matrix.index)

    # Step 6: Incorporate Likes/Dislikes of the Current User for Content-Based Filtering
    # Assume we have like/dislike data for the current user
    current_user_likes = {'6278e0e9-6ea7-4e34-8d08-43d81bce8ed1'}  # Example: Set of video_ids the current user liked
    current_user_dislikes = {'decad7c6-0d2f-4200-9d67-e69f7276db8e'}  # Example: Set of video_ids the current user disliked

    # Get the categories and authors of liked/disliked videos
    liked_videos_info = video_stats[video_stats['video_id'].isin(current_user_likes)]
    liked_categories = set(liked_videos_info['category_id'])
    liked_authors = set(liked_videos_info['author_id'])

    disliked_videos_info = video_stats[video_stats['video_id'].isin(current_user_dislikes)]
    disliked_categories = set(disliked_videos_info['category_id'])
    disliked_authors = set(disliked_videos_info['author_id'])

    # Step 7: Refine Recommendations Based on User Similarity and Likes/Dislikes
    def refine_recommendations(recommended_videos, liked_categories, liked_authors, disliked_categories, disliked_authors, video_stats):
        refined_recommendations = []
        
        for video_id in recommended_videos:
            video_info = video_stats[video_stats['video_id'] == video_id].iloc[0]
            category = video_info['category_id']
            author = video_info['author_id']
            
            # Boost videos that match liked categories or authors
            if category in liked_categories or author in liked_authors:
                refined_recommendations.append((video_id, 'boosted'))
            # Demote videos that match disliked categories or authors
            elif category in disliked_categories or author in disliked_authors:
                refined_recommendations.append((video_id, 'demoted'))
            else:
                refined_recommendations.append((video_id, 'neutral'))
        
        # Prioritize boosted videos, then neutral, then demoted
        refined_recommendations = sorted(refined_recommendations, key=lambda x: ('boosted', 'neutral', 'demoted').index(x[1]))
        return [video_id for video_id, _ in refined_recommendations]

    # Step 8: Recommend Videos for a User Based on Similar Users' Preferences
    def recommend_videos_for_user(user_id, similarity_matrix, user_video_matrix, video_stats, n_recommendations=N):
        # Check if the user exists in the matrix
        if user_id not in user_video_matrix.index:
            return f"User {user_id} not found in the dataset."
        
        # Get the user's row index
        user_idx = user_video_matrix.index.get_loc(user_id)
        
        # Get similarity scores for this user with other users
        similarity_scores = similarity_matrix[user_idx]
        
        # Sort users based on similarity scores in descending order (ignoring the user itself)
        similar_users = np.argsort(similarity_scores)[::-1][1:]

        # Get the videos the user has already watched
        user_watched_videos = set(user_video_matrix.columns[user_video_matrix.iloc[user_idx] > 0])
        
        # Create an empty dictionary to store recommended videos and their aggregated scores
        video_recommendations = {}
        
        # Loop through similar users and find videos they have watched but the current user hasn't
        for similar_user_idx in similar_users:
            similar_user_id = user_video_matrix.index[similar_user_idx]
            similar_user_watched_videos = set(user_video_matrix.columns[user_video_matrix.iloc[similar_user_idx] > 0])
            
            # Find videos that the similar user has watched but the current user hasn't
            recommended_videos = similar_user_watched_videos - user_watched_videos
            
            # Score the recommended videos by their similarity score
            for video_id in recommended_videos:
                if video_id not in video_recommendations:
                    video_recommendations[video_id] = 0
                video_recommendations[video_id] += similarity_scores[similar_user_idx]
            
            # Stop once we have enough recommendations
            if len(video_recommendations) >= n_recommendations:
                break
        
        # Sort recommended videos by their aggregated similarity scores
        sorted_recommendations = sorted(video_recommendations.items(), key=lambda x: x[1], reverse=True)
        recommended_videos = [video_id for video_id, score in sorted_recommendations[:n_recommendations]]
        
        # Refine recommendations based on the current user's likes/dislikes
        refined_recommendations = refine_recommendations(recommended_videos, liked_categories, liked_authors, disliked_categories, disliked_authors, video_stats)
        
        return refined_recommendations

    # Step 9: Example usage
    user_id = '0486f378-d285-4ea8-8a88-1f1119d7766a'  # Example user ID
    top_5_recommendations = recommend_videos_for_user(user_id=user_id, 
                                                    similarity_matrix=combined_user_similarity, 
                                                    user_video_matrix=user_video_matrix, 
                                                    video_stats=video_stats, 
                                                    n_recommendations=N)

    return top_5_recommendations
