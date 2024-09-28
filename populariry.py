import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd

def popularity(df_v, N):
    df_popular = df_v[['video_id','v_category_popularity_percent_30_days','v_category_popularity_percent_7_days','v_cr_click_vtop_30_days', 'v_cr_click_vtop_7_days', 'v_cr_click_vtop_1_days', 'v_total_comments', 'v_likes','v_dislikes' ]]

    def create_neural_network(input_shape):

        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(input_shape,)),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='linear')  # Выходной слой для прогноза популярности
        ])

        # Компиляция модели
        model.compile(
            loss='mean_squared_error',  # Функция потерь для регрессии
            optimizer='adam'  # Алгоритм оптимизации
        )

        return model


    # Разделение данных на входные признаки (X) и целевой признак (y)
    y = df_popular['video_id'].index  # Предсказываем id видео
    x = df_popular.drop(columns=['video_id'])


    # Создание нейронной сети
    model = create_neural_network(x.shape[1])

    # Обучение модели
    model.fit(x, y, epochs=50, verbose=0)  # Обучаем на 100 эпохах

    # Прогнозирование популярности
    predictions = model.predict(x)

    # Сортировка по прогнозу популярности (используем индексы)
    sorted_indices = predictions.argsort(axis=0)[::-1]
    # Получение 10 самых популярных ID видео
    top_N_videos = df_popular['video_id'].iloc[sorted_indices.flatten()[:N]].tolist()

    # Вывод результатов
    return top_N_videos

