import struct
import math
import socket
import time
import select

#creates an icmp packet with correct headers, but no payload
# icmp packet goes type(8) code(8) checksum(16), id(16) seq(16)
def create_icmp_packet (icmp_identifier):
    ICMP_ECHO_REQ_TYPE = 8
    ICMP_CODE = 0
    #creates ICMP header, checksum is 0 before calculating
    header = struct.pack('!BBHHH', ICMP_ECHO_REQ_TYPE,ICMP_CODE,0,icmp_identifier,1)
    #0 data payload
    data = bytes(0)
    check = checksum(header)
    #header with proper checksum value
    header = struct.pack('!BBHHH', ICMP_ECHO_REQ_TYPE,ICMP_CODE,check,icmp_identifier,1)
    packet = header + data
    return packet

#Calculates checksum value for ICMP header, sections off header into
#16 bit words and finds the sum
#Requires: 8 byte header
#Returns: one's complement checksum
def checksum(header_data):
    count = 0
    check = 0
    length = len(header_data)
    #checks size of header data to evenly separate it into 16 bit words
    #if required
    if length%2 != 0:
        header_data = header_data[0:length] + bytes(1)+header_data[length]
    while count <= length:
        check += int.from_bytes(header_data [count:(2+count)],'big') + int.from_bytes(header_data[(2+count):(4+count)],'big')
        count += 4
    check = check ^0xFFFF
    return check

#Sends one icmp packet through a socket
#requires packet: id, destination(hostname, port) TTL and socket
#returns nothing
def send_one_icmp_packet(id,destination,TTL,send_socket):

    return

#Recieves one ICMP packet through the socket input
#also sets a timeout and catches error in case of packet
#loss
def recv_one_icmp_packet(recv_socket):
    e = 0
    try:
        pkt,recv_data = recv_socket.recvfrom(1024)
    except socket.timeout:
        recv_data = (0,0)
        e = "Timeout occurred"

    return recv_data,e

#calculates time to send, then recieve 1 echo request packet
def ping_one(given_socket,id,destination,TTL,TIMEO):
    given_socket.setsockopt(socket.SOL_IP,socket.IP_TTL,TTL)
    given_socket.settimeout(TIMEO)
    given_socket.sendto(create_icmp_packet(id), destination)

    start_time = time.time()
    recv_data,error = recv_one_icmp_packet(given_socket)
    end_time = time.time()

    if error != 0:
        time_taken = '*'
    else:
        time_taken = round((end_time - start_time)* 1000)
    return time_taken,recv_data,error

#sends three ping requests to the destination
def ping_three (socket, id, destination, TTL, TIMEO):
    p1_time,recv_data1,error1 = ping_one(socket,id,destination,TTL,TIMEO)
    p2_time,recv_data2,error2 = ping_one(socket,id,destination,TTL,TIMEO)
    p3_time,recv_data3,error3 = ping_one(socket,id,destination,TTL,TIMEO)

    if recv_data1[0] !=0:
        display_data = recv_data1
        display_error = 0
        return display_data,p1_time,p2_time,p3_time,display_error

    elif recv_data2[0] != 0:
        display_data = recv_data2
        display_error = 0
        return display_data, p1_time, p2_time, p3_time, display_error

    elif recv_data3[0] != 0:
        display_data = recv_data3
        display_error = 0
        return display_data, p1_time, p2_time, p3_time, display_error

    else:
        display_data = ("",0)
        display_error = error1
        return display_data, p1_time, p2_time, p3_time, display_error

#starts the program
def main():
    #setting the variables needed, Timeout, TTL, Hops etc.
    icmp = socket.getprotobyname('icmp')
    TIMEO = 2
    id = 1
    TTL = 1
    MAX_HOPS = 30
    display_data = (0,0)

    #creating the socket used for the trace
    trace_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    print('Traceroute using python, enter a hostname to get started')
    hostname = input()

    try:
        ipaddr = socket.gethostbyname(hostname)
    except socket.gaierror:
        print("Hostname is invalid, try again")
        return

    print("Starting trace over a maximum of 30 hops")
    print("Tracing to %s [%s]" %(hostname,ipaddr))

    #Checks if TTL and data is correct
    while (TTL <= MAX_HOPS) and (display_data[0] != ipaddr):
        display_data,ping_time1,ping_time2,ping_time3,display_error  = ping_three(trace_socket,id,(hostname,1685),TTL,TIMEO)
        #checks if received data points to a server
        try:
            server = socket.gethostbyaddr(display_data[0])[0]
        except (socket.herror,socket.gaierror,OSError):
            server = ""

        if display_error != 0:
            print("%s   %s ms  %s ms  %s ms  %s" %(TTL,ping_time1,ping_time2,ping_time3,display_error))
        elif server != "":
            print(
                "%s   %s ms  %s ms %s ms %s [%s]" % (TTL, ping_time1, ping_time2, ping_time3, server, display_data[0]))
        else:
            print("%s   %s ms  %s ms %s ms %s " % (TTL, ping_time1, ping_time2, ping_time3, display_data[0]))
        TTL += 1
        id +=1
    trace_socket.close()

    return

main()





