from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import scipy.stats as stats
import numpy as np

class Continuous:
    def __init__(self, observed, predicted):
        self.observed = np.array(observed).reshape((len(observed),1))
        self.predicted = np.array(predicted).reshape((len(predicted),1))

    def mbe(self):
        diff = self.predicted - self.observed
        mbe = diff.mean()
        return mbe

    def mult_bias(self):
        obs_mean = (self.observed).mean()
        pred_mean = (self.predicted).mean()
        multbias = pred_mean / obs_mean
        return multbias

    def mae(self):
        mae = mean_absolute_error(self.observed, self.predicted)
        return mae

    def mse(self):
        mse = mean_squared_error(self.observed, self.predicted)
        return mse

    def rmse(self):
        rmse = np.sqrt(self.mse())
        return rmse

    def r2(self):
        r2 = r2_score(self.observed, self.predicted)
        return r2

    def pcc(self):
        pcc = (stats.pearsonr(np.squeeze(self.observed), np.squeeze(self.predicted)))[0]
        return pcc

    def metrics(self):
        mbe = self.mbe()
        mae = self.mae()
        mse = self.mse()
        rmse = self.rmse()
        pcc = self.pcc()

        return mbe, mae, mse, rmse, pcc


class Discrete:
    def __init__(self, observed, predicted):
        self.observed = np.array(observed).reshape((len(observed),1))
        self.predicted = np.array(predicted).reshape((len(predicted),1))
        self.hits = (self.tabulator())[0]
        self.misses = (self.tabulator())[1]
        self.false_alarms = (self.tabulator())[2]
        self.correct_negatives = (self.tabulator())[3]

    def tabulator(self):
        #Tabulation
        hits = 0
        misses = 0
        false_alarms = 0
        correct_negatives = 0

        for i in range(len(self.observed)):
            if (self.observed[i,0] == True) and (self.predicted[i,0] == True):
                hits += 1
            elif (self.observed[i,0] == False) and (self.predicted[i,0] == False):
                correct_negatives += 1
            elif (self.observed[i,0] == True) and (self.predicted[i,0] == False):
                false_alarms += 1
            else:
                misses += 1
    
        return hits, misses, false_alarms, correct_negatives

    def metrics(self):
        hits, misses, false_alarms, correct_negatives = self.tabulator()

        #Total Observations/Predictions
        total = hits + misses + false_alarms + correct_negatives
        
        #Accuracy
        accuracy = (hits + correct_negatives) / total
        
        #Frequency Bias
        freq_bias = (hits + false_alarms) / (hits + misses)
        
        #Hit Rate
        hit_rate = hits / (hits + misses)
        
        #False Alarm Ratio
        far = false_alarms / (hits + false_alarms)
        
        #Threat Score
        threat_score = hits / (hits + misses + false_alarms)
        
        return accuracy, freq_bias, hit_rate, far, threat_score


#Test
if __name__ == "__main__":
    #Continuous Data
    observed = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0]
    predicted = [0.5,2.1,3.0,4.0,5.0,6.7,7.8,8.9,9.0,10.0]

    #Continuous Variables
    print("Continuous Variables")
    temp_cont = Continuous(observed,predicted)
    print("MBE: " + str(temp_cont.mbe()))
    print("Metrics: ", end=" ")
    print(temp_cont.metrics())
    print('\n')
    
    #Discrete Data
    observed = [True, True, False, True, False,
                False, False, True, True, False]
    predicted = [True, True, True, False, False,
                False, True, False, True, False]
    
    #Discrete Variables
    print("Discrete Variables")
    rain_disc = Discrete(observed,predicted)
    print("Table: ", end=" ")
    print(rain_disc.tabulator())
    print("Metrics: ", end=" ")
    print(rain_disc.metrics())
    print("Hits: ", end=" ")
    print(rain_disc.hits)