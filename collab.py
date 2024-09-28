import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def collab(df, df1, N):
    logs = df1
    video_stats = df

    logs_clean = logs[['user_id', 'watchtime', 'video_id']]
    video_stats_clean = video_stats[['video_id', 'category_id', 'author_id']]

    merged_data = logs_clean.merge(video_stats_clean, on = 'video_id')

    user_video_matrix = merged_data.pivot_table(index='user_id', columns='video_id', values='watchtime', fill_value=0)
    user_category_matrix = pd.get_dummies(merged_data[['user_id', 'category_id']].set_index('user_id')['category_id'])
    user_author_matrix = pd.get_dummies(merged_data[['user_id', 'author_id']].set_index('user_id')['author_id'])

    user_similarity_watchtime = cosine_similarity(user_video_matrix)
    user_similarity_category = cosine_similarity(user_category_matrix)
    user_similarity_author = cosine_similarity(user_author_matrix)

    combined_user_similarity = (
        0.5 * user_similarity_watchtime +
        0.25 * user_similarity_category +
        0.25 * user_similarity_author
    )
    combined_user_similarity_df = pd.DataFrame(combined_user_similarity, 
                                            index=user_video_matrix.index, 
                                            columns=user_video_matrix.index)

    def recommend_videos_for_user(user_id, similarity_matrix, user_video_matrix, n_recommendations=5):
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
        
        # Return the top N recommendations
        return [video_id for video_id, score in sorted_recommendations[:n_recommendations]]

    # Step 9: Example usage
    user_id = '0486f378-d285-4ea8-8a88-1f1119d7766a'  # Example user ID
    top_N_recommendations = recommend_videos_for_user(user_id=user_id, 
                                                    similarity_matrix=combined_user_similarity, 
                                                    user_video_matrix=user_video_matrix, 
                                                    n_recommendations=N)

    print(top_N_recommendations)