import joblib
from sklearn import preprocessing

def predict_no_show(df):
    try:
        loaded_model = joblib.load('assets/Cart Model')
        trial_prediction = df.copy()
        trial_prediction = trial_prediction[['Day', 'Sms_Reminder', 'Waiting_Time', 'Appointment_Month',
                                             'Appointment_Week_Number', 'Age', 'Gender', 'Diabetes',
                                             'Drinks', 'HyperTension', 'Handicap', 'Smoker', 'Scholarship',
                                             'Tuberculosis', 'Show_Up']]
        trial_prediction = trial_prediction.reset_index(drop=True)
        Y_position = len(trial_prediction.columns) - 1  # Last column = Show Up
        X = trial_prediction.iloc[:, 0:Y_position]
        scaler = preprocessing.StandardScaler().fit(X)
        scaled_X_train = scaler.transform(X)
        y_pred = loaded_model.predict(scaled_X_train)

        df['Predicted'] = y_pred
        df['Predicted'] = df['Predicted'].astype('category')
    except:
        pass
    for each in ['Sms_Reminder','Diabetes', 'Drinks', 'HyperTension',
                 'Handicap', 'Smoker', 'Scholarship',
                 'Tuberculosis', 'Show_Up', 'Predicted'
                 ]:
        try:
            df[each] = df[each].apply(lambda x: 'Yes' if x == 1 else "No")
            df['Gender'] = df['Gender'].apply(lambda x: 'Female' if x == 0 else "Male")
        except:
            pass

    return df
