import random
from sklearn import svm
import numpy as np
from sklearn.model_selection import cross_val_score

from backend.FilesIO import FilesIO
from backend.Tokeniser import Tokeniser


"""

"""
class Classification:

    io = FilesIO()

    _dataFolder = 'data/'
    _keyWordsFolder = _dataFolder + 'lists/'
    _userPhrasesPath = _keyWordsFolder + 'User-keyPhrases.txt'
    _creatorPhrasesPath = _keyWordsFolder + 'Creator-keyPhrases.txt'


    def __init__(self, documentList):
        """

        """
        documents = documentList.getDocuments()
        trainDocuments = documentList.getTrainTestDocuments(0)
        testDocuments = documentList.getTrainTestDocuments(1)
        Xtrain, Ytrain = self.__formulateXY(trainDocuments, documentList)
        self._clf = self.__trainData(Xtrain, Ytrain)
        Xtest, Ytest = self.__formulateXY(testDocuments, documentList)
        self._testScore = self.__testData(Xtest, Ytest, testDocuments)
        self.__userCreatorRatings(testDocuments)
        self._crossValScore =                                                \
            self.__crossValidation(Xtrain, Xtest, Ytrain, Ytest)
        for document in documents:
            self.io.outputDocumentData(document)


    def getTestScore(self):
        """

        """
        return self._testScore

    def getCrossValScore(self):
        """

        """
        return self._crossValScore


    def __formulateXY(self, documents, documentList):
        """

        """
        allWords = documentList.deduceAllWords()
        X = np.zeros((len(documents), len(allWords)))
        Y = []
        for (r, document) in enumerate(documents):
            for (w, f) in document.getCount().getWordsCountZip():
                X[r][allWords.index(w)] = f
            Y.append(document.getClassInformation().getGt())
        return X, Y


    def __trainData(self, X, Y):
        """

        """
        clf = svm.SVC(gamma='scale', probability=True)
        clf.fit(X, Y)
        return clf

    def __testData(self, X, Y, testDocuments):
        """

        """
        probabilities = self._clf.predict_proba(X)
        for (r, document) in enumerate(testDocuments):
            document.getClassInformation().setHrRat(probabilities[r][0])
            document.getClassInformation().setIpRat(probabilities[r][1])
        return self._clf.score(X, Y)


    def __crossValidation(self, Xtrain, Xtest, Ytrain, Ytest):
        X = np.append(Xtrain, Xtest, axis=0)
        Y = Ytrain.copy()
        Y.extend(Ytest)
        crossValScore =                                                      \
            cross_val_score(estimator=self._clf, X=X, y=Y, cv=5)
        return crossValScore


    def __userCreatorRatings(self, documents):
        """

        """
        creatorPhrases = self.io.lineSeparatedToList(self._creatorPhrasesPath)
        userPhrases = self.io.lineSeparatedToList(self._userPhrasesPath)
        tokeniser = Tokeniser()
        for document in documents:
            text = document.getPDFtext().getText()
            sentences = tokeniser.splitBySentence(text)
            creatorSentences = tokeniser.removeSentencesWithoutPhrases(      \
                creatorPhrases, sentences)
            userSentences = tokeniser.removeSentencesWithoutPhrases(         \
                userPhrases, sentences)
            creatorProp = len(creatorSentences) / len(sentences)
            userProp = len(userSentences) / len(sentences)
            document.getClassInformation().setCreatorRat(creatorProp)
            document.getClassInformation().setUserRat(userProp)