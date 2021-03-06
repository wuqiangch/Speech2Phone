#!/usr/bin/env PYTHONIOENCODING="utf-8" python
import random
random.seed(5)
import tflearn
import os
import sys
import librosa
import numpy as np
import pickle

working =''



        
try:
    
    with open('Mfcc-Save/X_a_treino.pickle', 'rb') as f:
           X1 = pickle.load(f)
    

    with open('Mfcc-Save/X_b_treino.pickle', 'rb') as f:
           X2 = pickle.load(f)
       
    with open('Mfcc-Save/X_a_teste.pickle', 'rb') as f:
          Xt1 = pickle.load(f)
          
    with open('Mfcc-Save/X_b_teste.pickle', 'rb') as f:
          Xt2 = pickle.load(f)

          
    X = X1+X2
    Xtest = Xt1+Xt2
    
    #number of speakers 
    number_classes = 20
    
    
    #softmax transform data
    Y = []
    for i in range(len(X)):
            aux = [0]*number_classes
            aux[int(X[i][1])-1] =1
            Y.append(aux)

    Ytest = []
    for i in range(len(Xtest)):
            aux = [0]*number_classes
            aux[int(Xtest[i][1])-1] =1
            Ytest.append(aux)

    #ajustando X e Xtest, original formato [mfcc,locid], deixar apenas [mfcc] para treinar o modelo
    Aux = []
    for i in  range(len(X)):
            Aux.append([])
            Aux[i] = X[i][0]

    X= Aux
    Aux = []
    for i in  range(len(Xtest)):
            Aux.append([])
            Aux[i] = Xtest[i][0]

    Xtest= Aux
    



except:
    print("Base corrompida ou inexistente, verifique")
    exit()

net = tflearn.input_data(shape=[None, 13,216]) #Passando a data para o tf, 13 = n_mfcc; 44 = 1 segundo segment wave audio; None: o primeiro elemento deve ser None representando, o tamanho do lote.
net = tflearn.dropout(net, 0.6)
net = tflearn.fully_connected(net, number_classes*10,activation='elu')
net = tflearn.dropout(net, 0.6)
net = tflearn.fully_connected(net, number_classes*19,activation='relu')

net = tflearn.dropout(net, 0.6)
net = tflearn.fully_connected(net, number_classes, activation='softmax')#number_classes,  numero de locutores  para essa camada e 'softmax' nome ou função  de ativação para essa camada, default "linear"
#uma camada de regressão (a seguir à saída) é necessária como parte das operações de treinamento da estrutura.
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy',learning_rate=0.00005) # "adam" =  default gradient descent optimizer,loss= Função de perda utilizada por este otimizador de camada. Padrão: 'categorical_crossentropy'.

#criando a rede .
model = tflearn.DNN(net)
#trainando o modelo , x = input[Mfcc] , y = lista dos locutores, n_epoch = numero de etapas a serem executadas , show_metric=True: exibir a precisão a cada etapa , snapshot_step = 100 , terá 100 modelos instantâneos para cada etapa 
model.fit(X, Y, n_epoch=3000,shuffle=True, show_metric=True)


model.save('Save-Models/rna-tradicional-1.tflearn')


    
result = model.predict(Xtest)
res=0
c = 0 

#aredondando saida softmax
for i in range(len(result)):
    for x  in range(len(result[i])):
        result[i][x] = round(result[i][x])
        
        


for f,r in zip(Ytest, result):
    
    if np.all(f ==r):
         c = c + 1   


        
acc = float(c) / float(len(Xtest))

print('accuracy: %s' %str(acc),"de:",len(Xtest),' Acertou:',c)
print('treino instancias:',len(X),'teste instancias:',len(Xtest))
