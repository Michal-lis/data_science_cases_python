import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

# setting parameters for rc
plt.rc("font", size=14)

import seaborn as sns

from sklearn import preprocessing

sns.set(style='white')  # white beackground for seaborn plots
sns.set(style='whitegrid', color_codes=True)

train_df = pd.read_csv("train.csv")
test_df = pd.read_csv("test.csv")

print(train_df.head())
all_data = train_df.shape[0] + test_df.shape[0]
print('Train data is {} samples, {}% of all.'.format(train_df.shape[0], round(train_df.shape[0] / all_data * 100, 2)))
print('Test data is {} samples, {}% of all.'.format(test_df.shape[0], round(test_df.shape[0] / all_data * 100, 2)))

# DATA QUALITY
# checking how many missing values do we have
print(train_df.isnull().sum())

# AGE
# We can see that there are 177 Age missing, 687 Cabin missing and 2 Embarked missing
print('Percent of missing "Age" records is %.2f%%' % ((train_df['Age'].isnull().sum() / train_df.shape[0]) * 100))
# almost 20% of age data missing, lets visualise the age parameter
# from visualisation we can see than the histogram is skewed, so we will not use the median but the average value of age
# mean age
print('The mean of "Age" is %.2f' % (train_df["Age"].mean(skipna=True)))
# median age
print('The median of "Age" is %.2f' % (train_df["Age"].median(skipna=True)))

# CABIN
print('Percent of missing "Cabin" records is %.2f%%' % ((train_df['Cabin'].isnull().sum() / train_df.shape[0]) * 100))
# since 77% of Cabin data is missing, we will omit this information in our model

# EMBARKED
print('Per  cent of missing "Embarked" records is %.2f%%' % (
    (train_df['Embarked'].isnull().sum() / train_df.shape[0]) * 100))
# oly 2 data are missing out of 1200 so we will impute the most popular port

print('Boarded passengers grouped by port of embarkation (C = Cherbourg, Q = Queenstown, S = Southampton):')
print(train_df['Embarked'].value_counts())
# palette='Set2' defines the style
sns.countplot(x='Embarked', data=train_df, palette='Set2')
# plt.show()
# the most popular Embarked port is 'S' so Southampton, so I will impute this value into the mising ones

# DATA Wrangling
train_data = train_df.copy()
# inserting median of Age into the missing values:
train_data['Age'].fillna(train_df['Age'].median(skipna=True), inplace=True)
train_data['Embarked'].fillna(train_df['Embarked'].value_counts().idxmax(), inplace=True)
train_data.drop('Cabin', axis='columns', inplace=True)

# check if all the NULL values are gone
print(train_data.isnull().sum())

# Mergining two variables which are possibly multicollinear into one Variable ('TravellingAlone")
# train_data['TravelAlone'] = np.where((train_data['SibSp'] + train_data['Parch'] > 0, 0, 1))

# create categorical variables and drop some variables
training = pd.get_dummies(train_data, columns=["Pclass", "Embarked", "Sex"])
training
training.drop('Sex_female', axis='columns', inplace=True)
training.drop('PassengerId', axis='columns', inplace=True)
training.drop('Name', axis='columns', inplace=True)
training.drop('Ticket', axis='columns', inplace=True)

final_train = training
final_train.head()

# IMPORTANT: apply the same changes (median calculated on train data not on test data to the test data as you applied to the training data
test_data = test_df.copy()
test_data["Age"].fillna(train_df["Age"].median(skipna=True), inplace=True)
test_data["Fare"].fillna(train_df["Fare"].median(skipna=True), inplace=True)
test_data.drop('Cabin', axis=1, inplace=True)
test_data['Embarked'].fillna(train_df['Embarked'].value_counts().idxmax(), inplace=True)
# test_data['TravelAlone'] = np.where((test_data["SibSp"] + test_data["Parch"] > 0, 0, 1))
testing = pd.get_dummies(test_data, columns=["Pclass", "Embarked", "Sex"])
testing.drop('Sex_female', axis=1, inplace=True)
testing.drop('PassengerId', axis=1, inplace=True)
testing.drop('Name', axis=1, inplace=True)
testing.drop('Ticket', axis=1, inplace=True)

final_test = testing
final_test.head()

# Explanatory Data Anlysis - wizualizacje i stawianie pierwszych wniosków na podstawie wykresów itp
#
# zauważanie zależności np. to że gdy dziecko ma mniej niż 16 lat to większość z nich przeżywała -> stwórzmy osobną kategorię isMinor gdy wiek mniejsyz niż 16 lat
# #AGE
plt.figure(figsize=(15, 8))
ax = sns.kdeplot(final_train["Age"][final_train.Survived == 1], color="darkturquoise", shade=True)
sns.kdeplot(final_train["Age"][final_train.Survived == 0], color="lightcoral", shade=True)
plt.legend(['Survived', 'Died'])
plt.title('Density Plot of Age for Surviving Population and Deceased Population')
ax.set(xlabel='Age')
plt.xlim(-10, 85)
# plt.show()
final_train['IsMinor'] = np.where(final_train['Age'] <= 16, 1, 0)
final_test['IsMinor'] = np.where(final_test['Age'] <= 16, 1, 0)

# FARE
plt.figure(figsize=(15, 8))
ax = sns.kdeplot(final_train["Fare"][final_train.Survived == 1], color="darkturquoise", shade=True)
sns.kdeplot(final_train["Fare"][final_train.Survived == 0], color="lightcoral", shade=True)
plt.legend(['Survived', 'Died'])
plt.title('Density Plot of Fare for Surviving Population and Deceased Population')
ax.set(xlabel='Fare')
plt.xlim(-20, 200)
# plt.show()
# we can see that the passangers who paid less for their ticket are more likely to die

# Passenger Class
sns.barplot('Pclass', 'Survived', data=train_df, color="darkturquoise")
# plt.show()
# Being in the first class tuns out to be the safest

# Embarked Port
sns.barplot('Embarked', 'Survived', data=train_df, color="darkturquoise")
# LOGISTIC REGRESSION

from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE

cols = ["Age", "Fare", "SibSp", "Parch", "Pclass_1", "Pclass_2", "Embarked_C", "Embarked_S", "Sex_male", "IsMinor"]
X = final_train[cols]
y = final_train['Survived']

model = LogisticRegression()
# 8 is the number of attributes we want to reach
rfe = RFE(model, 8)
rfe = rfe.fit(X, y)

# RFECV -  find the optimal number of features
from sklearn.feature_selection import RFECV

rfecv = RFECV(estimator=LogisticRegression(), step=1, cv=10, scoring='accuracy')
rfecv.fit(X, y)

print("Optimal number of features: %d" % rfecv.n_features_)
print('Selected features: %s' % list(X.columns[rfecv.support_]))

Selected_features = list(X.columns[rfecv.support_])
X = final_train[Selected_features]
plt.subplots(figsize=(8, 5))
sns.heatmap(X.corr(), annot=True, cmap="RdYlGn")
plt.show()

# MODEL EVALUATION
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, confusion_matrix, \
    precision_recall_curve, roc_curve, auc, log_loss

X = final_train[Selected_features]
y = final_train['Survived']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2)
# Log reg

logreg = LogisticRegression()
# trenowanie
logreg.fit(X_train, y_train)
# predykcja
y_pred = logreg.predict(X_test)
y_pred_proba = logreg.predict_proba(X_test)[:, 1]
[fpr, tpr, thr] = roc_curve(y_test, y_pred_proba)
print('Train/Test split results:')
print(logreg.__class__.__name__ + " accuracy is %2.3f" % accuracy_score(y_test, y_pred))
print(logreg.__class__.__name__ + " log_loss is %2.3f" % log_loss(y_test, y_pred_proba))
print(logreg.__class__.__name__ + " auc is %2.3f" % auc(fpr, tpr))

idx = np.min(np.where(tpr > 0.95))  # index of the first threshold for which the sensibility > 0.95

plt.figure()
plt.plot(fpr, tpr, color='coral', label='ROC curve (area = %0.3f)' % auc(fpr, tpr))
plt.plot([0, 1], [0, 1], 'k--')
plt.plot([0, fpr[idx]], [tpr[idx], tpr[idx]], 'k--', color='blue')
plt.plot([fpr[idx], fpr[idx]], [0, tpr[idx]], 'k--', color='blue')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (1 - specificity)', fontsize=14)
plt.ylabel('True Positive Rate (recall)', fontsize=14)
plt.title('Receiver operating characteristic (ROC) curve')
plt.legend(loc="lower right")
plt.show()

print("Using a threshold of %.3f " % thr[idx] + "guarantees a sensitivity of %.3f " % tpr[idx] +
      "and a specificity of %.3f" % (1 - fpr[idx]) +
      ", i.e. a false positive rate of %.2f%%." % (np.array(fpr[idx]) * 100))

final_test['Survived'] = log_clf.predict(final_test[Selected_features])
final_test['PassengerId'] = test_df['PassengerId']

submission = final_test[['PassengerId', 'Survived']]

submission.to_csv("submission.csv", index=False)

submission.tail()
