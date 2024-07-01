from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import csv
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def Train():
    with open('/home/pi/CREALITS/traindata/train.csv', mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for i in range(0, 7):
            RGBs = []
            for f in listdir('/home/pi/CREALITS/traindata/'):
                fpath = join('/home/pi/CREALITS/traindata/', f)
                isfile(fpath)

                image = cv2.imread(fpath)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                if contours[i] and contours[i] > 0:
                    mask = np.zeros_like(gray)
                    cv2.drawContours(mask, [contours[i]], -1, 255, thickness=cv2.FILLED)

                    RGBs.append(cv2.mean(image, mask=mask)[:3])
            
            writer.writerow(RGBs)
        
        reader = np.array(csv.reader(csv_file, delimiter=','))
        
        X = reader[:, :3]
        y = reader[:, -1]

        # Split data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create and train the model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Mean Squared Error: {mse}")
        print(f"R^2 Score: {r2}")

        # Visualize the results
        plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual')
        plt.xlabel('Actual values')
        plt.ylabel('Predicted values')
        plt.title('Linear Regression with RGB Input')
        plt.legend()
        plt.show()



if __name__ == "__main__":
    Train()