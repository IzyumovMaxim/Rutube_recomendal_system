import pandas as pd

def star(df):
    l = [df["v_year_views"].tolist(), df['v_month_views'].tolist(), df['v_week_views'].tolist(), df['v_day_views'].tolist()]

    avt = [df['v_frac_avg_watchtime_1_day_duration'].tolist(), df['v_frac_avg_watchtime_7_day_duration'].tolist(), df['v_frac_avg_watchtime_30_day_duration'].tolist()]
    dur = df['v_duration'].tolist()
    star = {
        "Video_ID": df['video_id'].tolist(),
        "Growth score": [],
        "Retention score": [],
        "Overall score": []
    }
    for i in range(len(df["v_year_views"].tolist())):
        # views score
        c = [l[0][i], l[1][i], l[2][i], l[3][i]]
        if c[0] != 0:
            gm = c[1] / (c[0]/12)
        else:
            gm = 0
        if c[1] != 0:
            gw = c[2] / (c[1]/4.3)
        else:
            gw = 0
        if c[2] != 0:
            gd = c[3] / (c[2]/7)
        else:
            gd = 0
        if c[1] == c[2]:
            gw = 0
        s = 0.5*gd + 0.4*gw + 0.1*gm
        # retention score
        if avt[0][i] > 0 and avt[1][i] > 0 and avt[2][i] > 0 and dur[i] != 0:
            rw = avt[1][i] / (avt[2][i]/4.3)
            rd = avt[0][i] / (avt[1][i]/7)
            R = (rw + rd) / 2
        else:
            R = 0
        O = 0.2*R + 0.8*s

        # star["Growth score"].append(s)
        # star["Retention score"].append(R)
        star['Overall score'].append(O)
    star_res = pd.DataFrame(star) 
    
    return star_res
