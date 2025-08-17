import threading

ips_bby = ['192', '827', '2726']

def fucn(ip_lis):
    for ip in ip_lis:
        threading.Thread(target=prints, args=(ip, )).start()
        print("called")
        
      
def prints(ips):
    item = ips
    print(item)  
      
      
        
fucn(ips_bby)