import pandas as pd
import datetime

def T(df_05, df_06, df_v,amount_videos):
    amount_videos = 5

    df_v_cat = df_v[['video_id', 'categor   y_id']]
    df_v_cat
    df_t = pd.DataFrame()
    df_t = pd.concat([df_05, df_06], axis=0, ignore_index=True)
    df_t = df_t.drop(columns=['user_id', 'region', 'city','watchtime'])
    df_t = df_t.merge(df_v_cat, on='video_id', how='left')

    def get_day_of_week(df, date_column_name):
        df[date_column_name] = pd.to_datetime(df[date_column_name])
        df['week day'] = df[date_column_name].dt.weekday
        return df

    df = df_t[['event_timestamp']]

    df = get_day_of_week(df, 'event_timestamp')
    df = df.drop(columns=['event_timestamp'])
    print(df)
    df_t['week day'] = df
    df_t = df_t.drop(columns=['event_timestamp'])

    def get_most_viewed_videos(df, current_day_of_week, amount_videos):
        filtered_df = df[df['week day'] == current_day_of_week]
        view_counts = filtered_df.groupby('category_id')['video_id'].count()
        sorted_counts = view_counts.sort_values(ascending=False)
        top_categories = sorted_counts.index[:amount_videos].tolist()
        top_videos = filtered_df[filtered_df['category_id'].isin(top_categories)].groupby('video_id').size().sort_values(ascending=False).index[:amount_videos].tolist()
        return top_videos

    today = datetime.datetime.today().weekday()
    top_videos = get_most_viewed_videos(df_t, today, amount_videos)
    return top_videos