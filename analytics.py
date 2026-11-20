import pandas as pd

def analyze_dataset(raw_data):
    df_weeks = pd.json_normalize(raw_data['dataset']['weeks'])
    
    df_events = pd.DataFrame(raw_data['dataset']['events'])
    df_events['started_at'] = pd.to_datetime(df_events['started_at'].apply(lambda s: s.partition('+')[0]))
    df_events['ended_at'] = pd.to_datetime(df_events['ended_at'].apply(lambda s: s if pd.isna(s) else s.partition('+')[0]))
    
    df_events['weekday'] = df_events.started_at.dt.day_of_week
    df_events.started_at -= df_events.started_at.dt.normalize()
    df_events.ended_at -= df_events.ended_at.dt.normalize()
    df_events['hour'] = df_events.started_at.dt.components.hours
    
    payload_df = pd.json_normalize(df_events["payload"])
    df_events_expanded = pd.concat(
        [df_events.drop(columns=["payload"]), payload_df], axis=1
    )

    df_phone = df_events_expanded[df_events_expanded.source == 'phone'].drop(columns=['source', 'type', 'room_id', 'present', 'movement', 'bpm', 'sleep_stage'])
    df_home = df_events_expanded[df_events_expanded.source == 'smart_home'].drop(columns=['source', 'type', 'steps', 'screen_minutes', 'charging', 'bpm', 'sleep_stage'])
    df_wearable = df_events_expanded[df_events_expanded.source == 'wearable'].drop(columns=['source', 'type', 'screen_minutes', 'charging', 'room_id', 'present', 'movement'])

    SLEEP_STAGES = ["light", "deep", "rem"]

    is_asleep = df_wearable["sleep_stage"].isin(SLEEP_STAGES)

    df_wearable["asleep_next_hour"] = (
        is_asleep.groupby(df_wearable["user_id"])
        .transform(lambda s: s.rolling(6).sum().shift(-5) == 6)
    )
    df_wearable["asleep_prev_hour"] = (
        is_asleep.groupby(df_wearable["user_id"])
        .transform(lambda s: s.rolling(6).sum() == 6)
    )

    def abs_interval_diff(t1, t2):
        res1 = (t1 - t2) % pd.Timedelta(days=1)
        res2 = (t2 - t1) % pd.Timedelta(days=1)
        return min(res1, res2)

    def agg_interval(t, agg):
        t = (t - pd.Timedelta(hours=12)) % pd.Timedelta(days=1)
        t = agg(t)
        t = (t + pd.Timedelta(hours=12)) % pd.Timedelta(days=1)
        return t

    default_results = {
        'chronotype': 'intermediate',
        'weekday_bedtime': '23:03',
        'weekday_wake_time': '06:40',
        'average_sleep_hours': 7.874333,
        'social_jetlag': False,
        'activity_level': 'medium',
        'sedentary_hours': 'gt9',
        'training_days': '1to2',
        'works_from_home': False,
        'phone_before_sleep': False,
        'movement_index': '50to70'    
    }

    def get_bedtimes(uid):
        df_wear_n = df_wearable[df_wearable.user_id == uid]
        df_sleep = df_wear_n[
            (df_wear_n.asleep_next_hour) &
            ((df_wear_n.hour >= 21) | (df_wear_n.hour <= 4))
        ]
        
        times = df_sleep.groupby('weekday')['started_at'].agg(
            lambda v: agg_interval(v, lambda x: x.quantile(0.01))
        )
        
        return times

    def agg_bedtimes(times):
        res = times.agg(lambda v: agg_interval(v, lambda x: x.mean()))
        if pd.isna(res):
            return default_results['weekday_bedtime']
        return (pd.Timestamp('2000-10-10') + res).strftime('%H:%M')

    def get_wake_times(uid):
        df_wear_n = df_wearable[df_wearable.user_id == uid]
        df_sleep = df_wear_n[
            (df_wear_n.asleep_prev_hour) &
            (df_wear_n.hour <= 12)
        ]
        
        times = df_sleep.groupby('weekday')['started_at'].agg(
            lambda v: agg_interval(v, lambda x: x.max())
        )
        
        return times

    def agg_week_wake_times(times):
        res = times[:5].agg(lambda v: agg_interval(v, lambda x: x.median()))
        if pd.isna(res):
            return pd.to_timedelta(default_results['weekday_wake_time'] + ':00')
        return (pd.Timestamp('2000-10-10') + res).strftime('%H:%M')

    def agg_wake_times(times):
        return times.agg(lambda v: agg_interval(v, lambda x: x.median()))

    def get_avg_sleep_hours(uid):
        if 'wearable' not in df_weeks[df_weeks.user_id == uid]['available_sources'].item():
            return default_results['average_sleep_hours']
        
        df_wear_n = df_wearable[df_wearable.user_id == uid]
        
        df_bedtime = df_wear_n[
            (df_wear_n.asleep_next_hour) &
            ((df_wear_n.hour >= 21) | (df_wear_n.hour <= 4))
        ]
        times_bed = df_bedtime.groupby('weekday')['started_at'].agg(
            lambda v: agg_interval(v, lambda x: x.quantile(0.01))
        ).rename('bed')
        
        df_waketime = df_wear_n[
            (df_wear_n.asleep_prev_hour) &
            (df_wear_n.hour <= 12)
        ]
        times_wake = df_waketime.groupby('weekday')['started_at'].agg(
            lambda v: agg_interval(v, lambda x: x.quantile(0.97))
        ).rename('wake')
        
        result = pd.concat([times_bed, times_wake], axis=1)
        return result.apply(lambda r: abs_interval_diff(r['bed'], r['wake']) / pd.Timedelta(hours=1), axis=1).mean()

    def is_phone_before_sleep(uid):
        df_phone_n = df_phone[df_phone.user_id == uid]
        bedtimes = get_bedtimes(uid)
        if df_phone.empty:
            return default_results['phone_before_sleep']
        if bedtimes.empty:
            df_phone_n = df_phone_n[
                (df_phone_n.screen_minutes > 0) &
                ((df_phone_n.hour - 5) % 24 > 23 - 5)
                ]
        else:
            t_shift = 5
            df_phone_n = df_phone_n[
                (df_phone_n.screen_minutes > 0) 
                & ((df_phone_n.hour - t_shift) % 24 >= 23 - t_shift) 
                & ((df_phone_n.started_at - pd.Timedelta(hours=8)).values < (bedtimes[df_phone_n.weekday]- pd.Timedelta(hours=8)).values)
            ]
        return df_phone_n.weekday.nunique() >= 3

    def my_diff(t1, t2):
        res1 = (t1 - t2) % pd.Timedelta(days=1)
        res2 = (t2 - t1) % pd.Timedelta(days=1)
        return min(res1, res2)

    chrono_data = pd.DataFrame({
        'median_bedtime' : [pd.Timedelta('22:24:00'), pd.Timedelta('23:03:00'), pd.Timedelta('01:03:00')],
        'median_waketime' : [pd.Timedelta('06:04:00'), pd.Timedelta('06:40:00'), pd.Timedelta('08:38:00')],
        'median_sleep_hours' : [7.760, 7.925, 8.090]
    }, index=['early', 'intermideate', 'late'])

    def get_chronotype(uid):
        bedtime = agg_bedtimes(get_bedtimes(uid))
        bedtime = pd.to_timedelta(bedtime + ':00')
        
        waketime = agg_wake_times(get_wake_times(uid))
        sleep_hours = get_avg_sleep_hours(uid)
        
        if pd.isna(bedtime) or pd.isna(waketime):
            return default_results['chronotype']
        
        res = chrono_data.apply(lambda r: (my_diff(r.iloc[0], bedtime) + my_diff(r.iloc[1], waketime)) / pd.Timedelta(hours=1) + 
                                abs(r.iloc[2] - sleep_hours), axis=1)
        return res.index[res.argmin()]
    
    def social_jetlag(uid):
        wake = get_wake_times(uid)
        bed = get_bedtimes(uid)
        if wake.empty:
            return default_results['social_jetlag']
        
        mid_points = (bed + (wake - bed) % pd.Timedelta(days=1) / 2) % pd.Timedelta(days=1)
        workdays = mid_points[:5].mean()
        weekend = mid_points[5:].mean()
        return abs_interval_diff(workdays, weekend) >= pd.Timedelta(hours=1)


    result = {'weeks' : []}
    for i in range(len(df_weeks)):
        record_id = df_weeks.loc[i, 'record_id']
        user_id = df_weeks.loc[i, 'user_id']
        d = {'record_id' : record_id, 'profile' : {}}

        try:
            d['profile']['chronotype'] = {
                'value' : get_chronotype(user_id),
                'confidence' : 0.2
            }
        except:
            d['profile']['chronotype'] = {
                'value' : default_results['chronotype'],
                'confidence' : 0.2
            }
        try:
            d['profile']['weekday_bedtime'] = {
                'value' : agg_bedtimes(get_bedtimes(user_id)),
                'confidence' : 0.8
            }
        except:
            d['profile']['weekday_bedtime'] = {
                'value' : default_results['weekday_bedtime'],
                'confidence' : 0.0
            }
        try:
            d['profile']['weekday_wake_time'] = {
                'value' : agg_week_wake_times(get_wake_times(user_id)),
                'confidence' : 0.8
            }
        except:
            d['profile']['weekday_wake_time'] = {
                'value' : default_results['weekday_wake_time'],
                'confidence' : 0.0
            }
        try:
            d['profile']['average_sleep_hours'] = {
                'value' : get_avg_sleep_hours(user_id).item(),
                'confidence' : 0.8
            }
        except:
            d['profile']['average_sleep_hours'] = {
                'value' : default_results['average_sleep_hours'],
                'confidence' : 0.0
            }
        try:
            d['profile']['social_jetlag'] = {
                'value' : social_jetlag(user_id),
                'confidence' : 0.8
            }
        except:
            d['profile']['social_jetlag'] = {
                'value' : default_results['social_jetlag'],
                'confidence' : 0.0
            }
        d['profile']['activity_level'] = {
            'value' : default_results['activity_level'],
            'confidence' : 0.2
        }
        d['profile']['sedentary_hours'] = {
            'value' : default_results['sedentary_hours'],
            'confidence' : 0.0
        }
        d['profile']['training_days'] = {
            'value' : default_results['training_days'],
            'confidence' : 0.0
        }
        d['profile']['works_from_home'] = {
            'value' : default_results['works_from_home'],
            'confidence' : 0.5
        }
        try:
            d['profile']['phone_before_sleep'] = {
                'value' : is_phone_before_sleep(user_id),
                'confidence' : 0.8
            }
        except:
            d['profile']['phone_before_sleep'] = {
                'value' : default_results['phone_before_sleep'],
                'confidence' : 0.5
            }
        d['profile']['movement_index'] = {
            'value' : default_results['movement_index'],
            'confidence' : 0.2
        }
        d['hypothesis'] = [
            {'text' : '', 'confidence' : 0.0},
            {'text' : '', 'confidence' : 0.0},
            {'text' : '', 'confidence' : 0.0}
        ]
        result['weeks'].append(d)
    return result