import threading

ips_bby = ['192', '827', '2726']

ports = ["10", "90" ,"80", "80"]

def fucn(ip_lis, port):
    for ip in ip_lis:
        threading.Thread(target=prints, args=(ip, port,)).start()
        print("called")
        
      
def prints(ips, portt):
    ports = portt
    port_lenmax = len(portt)
    item = ips
    print(f"{item} \n {ports[:2]} HELLOOOO")  
      
      
        
fucn(ips_bby, ports)