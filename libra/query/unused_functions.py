# def stats(
#     dataset=None,
#     drop=None,
#     column_name=None,
# ):
#     logger("Reading in dataset....")
#     # Reading in dataset and creating pdtabulate variable to format outputs
#     dataReader = DataReader(dataset)
#     data = dataReader.data_generator()

#     if drop is not None:
#         data.drop(drop, axis=1, inplace=True)

#     data.fillna(0, inplace=True)
#     logger("Creating lambda object to format...")

#     def pdtabulate(df):
#         return tabulate(
#             df, headers='keys', tablefmt='psql')

#     logger("Identifying columns to transform....")

#     # identifying categorical and numerical columns, and encoding
#     # appropriately
#     categor = data.select_dtypes(exclude=['int', 'float'])
#     categor = categor.apply(LabelEncoder().fit_transform)
#     for value in categor.columns:
#         data[str(value)] = categor[str(value)]

#     # if user doesn't specify column analysis on performed on the whole
#     # dataset
#     if column_name == "none":
#         columns = []
#         sim = []
#         for first_val in data.columns:
#             for sec_val in data.columns:
#                 if first_val == sec_val:
#                     continue
#                 columns.append(str(first_val) + "_" + str(sec_val))
#                 sim.append(1 - cosine(data[first_val], data[sec_val]))
#             df = pd.DataFrame(columns=columns)
#             df.loc[len(df)] = sim

#             cols = []
#             vals = []
#             logger("Restructuring dataset for similarity...")
#             # identifying top 5 feature importances and appending them to an
#             # array for display
#             for val in np.argpartition(np.asarray(df.iloc[0]), -5)[-5:]:
#                 cols.append(df.columns[val])
#                 vals.append(df[df.columns[val]].iloc[0])
#                 frame = pd.DataFrame(columns=cols)
#                 frame.loc[len(df)] = vals
#             print("Similarity Spectrum")
#             print(pdtabulate(frame))
#             print()
#             print("Dataset Description")
#             print(pdtabulate(data.describe()))

#         else:
#             logger("Performing similarity calculations....")
#             columns = []
#             sim = []
#             # identifying columns to be compared
#             for val in data.columns:
#                 if val == column_name:
#                     continue
#                 columns.append(str(column_name) + "_" + str(val))
#                 sim.append(1 - cosine(data[column_name], data[val]))
#             df = pd.DataFrame(columns=columns)
#             df.loc[len(df)] = sim

#         cols = []
#         vals = []
#         # identifying top 5 feature importances and appending them to a
#         # dataset
#         for val in np.argpartition(np.asarray(df.iloc[0]), -5)[-5:]:
#             cols.append(df.columns[val])
#             vals.append(df[df.columns[val]].iloc[0])
#             frame = pd.DataFrame(columns=cols)
#             frame.loc[len(df)] = vals

#         # displaying the similarity spectrum and the formatted
#         # data.describe()
#     print("Similarity Spectrum")
#     print("-------------------------")
#     print(pdtabulate(frame))
#     print()
#     print("Dataset Description")
#     print("-------------------------")
#     print(pdtabulate(data[column_name]).describe())


#def booster(instruction,dataset,y,target="",obj):
#    #obj=["reg:linear","multi:softmax "]
#    if target == "":
#        y=data_y(instruction)
#
#    X_train, X_test, y_train, y_test = train_test_split(
#    dataset, y, test_size=0.2, random_state=49)
#    clf = XGBClassifier(objective=obj,learning_rate =0.1,silent=1,alpha = 10)
#    clf.fit(X_train, y_train)
#    y_pred=clf.predict(X_test)
#    return accuracy_score(y_pred, y_test), y_pred 
#    #importance graph
#   feature_important = model.get_booster().get_score(importance_type='weight')
#   keys = list(feature_important.keys())
#   values = list(feature_important.values())
#
#   data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by = "score", ascending=False)
#   data.plot(kind='barh')


#Squeezenet
"""
from keras_squeezenet import SqueezeNet
from keras.models import Model
from keras.layers import  Convolution2D, MaxPooling2D, Lambda
from keras.layers import Activation, GlobalAveragePooling2D, concatenate
from keras.losses import categorical_crossentropy as logloss
from keras.metrics import categorical_accuracy, top_k_categorical_accuracy
from keras import backend
from keras import optimizers

temperature, lambda_const = 5.0, 0.2
num_classes=2
def knowledge_distillation_loss(y_true, y_pred, lambda_const,num_classes):
    y_true, logits = y_true[:, :num_classes], y_true[:, num_classes:]
    y_soft = backend.softmax(logits/temperature)
    y_pred, y_pred_soft = y_pred[:, :num_classes], y_pred[:, num_classes:]    
    return lambda_const*logloss(y_true, y_pred) + logloss(y_soft, y_pred_soft)

def accuracy(y_true, y_pred):
    y_true = y_true[:, :num_classes]
    y_pred = y_pred[:, :num_classes]
    return categorical_accuracy(y_true, y_pred)

def top_5_accuracy(y_true, y_pred):
    y_true = y_true[:, :num_classes]
    y_pred = y_pred[:, :num_classes]
    return top_k_categorical_accuracy(y_true, y_pred)

def categorical_crossentropy(y_true, y_pred):
    y_true = y_true[:, :num_classes]
    y_pred = y_pred[:, :num_classes]
    return logloss(y_true, y_pred)

# logloss with only soft probabilities and targets
def soft_logloss(y_true, y_pred):     
    logits = y_true[:, num_classes:]
    y_soft = backend.softmax(logits/temperature)
    y_pred_soft = y_pred[:, num_classes:]    
    return logloss(y_soft, y_pred_soft)

def get_snet_layer(num_out=2):
    global num_outputs
    num_outputs=num_out
    model = SqueezeNet()

    # remove softmax
    model.layers.pop()
    # usual probabilities
    logits = model.layers[-1].output
    probabilities = Activation('softmax')(logits)
    # softed probabilities
    logits_T = Lambda(lambda x: x/temperature)(logits)
    probabilities_T = Activation('softmax')(logits_T)

    output = concatenate([probabilities, probabilities_T])
    model = Model(model.input, output)
    model.compile(
        optimizer=optimizers.SGD(lr=1e-2, momentum=0.9, nesterov=True), 
        loss=lambda y_true, y_pred: knowledge_distillation_loss(y_true, y_pred, lambda_const), 
        metrics=[accuracy, top_5_accuracy, categorical_crossentropy, soft_logloss]
    )
    return model

model= get_snet_layer(num_classes)
history = model.fit_generator(
        X_train, 
        steps_per_epoch=X_train.n //
        X_train.batch_size, epochs=25,verbose=0,
        callbacks=[
            EarlyStopping(monitor='val_accuracy', patience=4, min_delta=0.01),
            ReduceLROnPlateau(monitor='val_accuracy', factor=0.1, patience=2, epsilon=0.007)
        ],
        validation_data=X_test, validation_steps=X_test.n //
        X_test.batch_size, workers=4
    )
"""









# # Checks columns for text
# # Converts text to numbers using TF-IDF
# def process_text(data):
#
#     combined = pd.concat([data['train'], data['test']], axis=0)
#
#     combined.dropna(inplace=True)
#
#     possible_text_cols = combined.select_dtypes(
#         exclude=["number"]).columns
#     text_cols = list()
#
#     # Scans categorical columns for text
#     for col in possible_text_cols:
#         print(len(pd.unique(combined[col])))
#         print(len(combined))
#         print("\n\n")
#         if len(np.unique(combined[col])) == len(combined):
#             text_cols.append(col)
#
#     print(text_cols)
#     #text_preprocessing()


# Returns True if text has more than 3 spaces
# Otherwise false
# def find_spaces(text):
#     spaces = 0
#     for i in text:
#         if spaces > 3:
#             return True
#         if i.isspace():
#             spaces += 1
#     return False


"""
        trainingImages = []
        train_labels = []
        validationImages = []
        test_labels = []

        for path in imgPaths:
        classLabel = path.split(os.path.sep)[-2]
        classes.add(classLabel)
        img = img_to_array(load_img(path, target_size=(64, 64)))

        if path.split(os.path.sep)[-3] == 'training_set':
            trainingImages.append(img)
            train_labels.append(classLabel)
        else:
            validationImages.append(img)
            test_labels.append(classLabel)

        trainingImages = np.array(trainingImages)
        train_labels = to_categorical(np.array(train_labels))
        validationImages = np.array(validationImages)
        test_labels = to_categorical(np.array(test_labels))
        model.compile(loss=’categorical_crossentropy’,
                  optimizer=’sgd’,
                  metrics=[‘accuracy’])
        history=model.fit(train_images, train_labels,
                  batch_size=100,
                  epochs=5,
                  verbose=1)
        """


# Seperates the color channels and then reshapes each of the channels to
# (224, 224)
# def processColorChanel(img):
#     b, g, r = cv2.split(img)
#     # seperating each value into a color channel and resizing to a standard
#     # size of 224, 224, 3 <- because of RGB color channels. If it's not 3
#     # color channels it'll pad with zeroes
#     b = cv2.resize(b, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
#     g = cv2.resize(g, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
#     r = cv2.resize(r, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
#     img = cv2.merge((b, g, r))
#     return img

# # returns metrics about your dataset including similarity information
# def stat_analysis(self, column_name="none", drop=None):
#     stats(
#         dataset=self.dataset,
#         drop=drop,
#         column_name=column_name
#     )
#
#     return
