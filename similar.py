
def similar(df):
    group = df[['video_id', 'category_id']]
    def recommend_videos_same_category(current_video_id):
        video_stat_df = group
        
        # Step 2: Find the category of the current video being watched
        current_video_info = video_stat_df[video_stat_df['video_id'] == current_video_id]
        
        if current_video_info.empty:
            return f"Video with ID {current_video_id} not found."
        
        current_category_id = current_video_info['category_id'].values[0]
        
        # Step 3: Filter all videos from the same category
        same_category_videos = video_stat_df[video_stat_df['category_id'] == current_category_id]
        
        # Step 4: Return a list of video IDs and titles from the same category
        recommended_videos = same_category_videos[['video_id']].reset_index(drop=True)
        
        return recommended_videos

    # Example usage:
    current_video_id = '470b4e3e-e06d-4370-80dc-34d6a78b22db' # Replace with the actual video_id being watched
    recommendations = recommend_videos_same_category(current_video_id)
    return recommendations
