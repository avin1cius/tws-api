from ibapi.client import EClient #Outgoing messages
from ibapi.wrapper import EWrapper #Incoming messages
import time
import threading
import csv

hostname = "127.0.0.1"
socket_port = 4001 #IBGW 4001, TWS 7496

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.dictAccountSummary = {}
        
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        print(f"{account}\t, {tag}: {value}\t {currency}")
        if account in self.dictAccountSummary:
            self.dictAccountSummary[account].append(value) #NetLiquidation
        else: #Create key
            self.dictAccountSummary[account] = []
            self.dictAccountSummary[account].append(value) #GrossPositionValue
        
    def accountSummaryEnd(self, reqId: int):
        print(f"\nRequest {reqId} has been finished")
        self.disconnect()
        print("Disconnected from API")
        
def main():
    
    app = IBApi()
    try:
        while True:        
            app.connect(hostname, socket_port, 0)
            time.sleep(3)
            print(f'Connected to {hostname}:{socket_port}')
            app.reqAccountSummary(9001, "All", "GrossPositionValue, NetLiquidation")
               
            time.sleep(3)
            app.run()
         
            listLeverage = []
            leverage = 0
            for x in app.dictAccountSummary: 
                if  float(app.dictAccountSummary[x][1]): #Compute Leverage only when NetLiquidation != 0
                    leverage = float(app.dictAccountSummary[x][0])/float(app.dictAccountSummary[x][1])
                    listLeverage.append((x, leverage))
                else: listLeverage.append((x, 0))

            with open('Leverage.csv', 'w', newline='') as csvfile:
                fieldnames = ['Account', 'Leverage']
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                writer.writerows(listLeverage)
            print("Sleeping for 3 minutes\n")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Bye!")
        return
    
if __name__ == "__main__":
    main()
