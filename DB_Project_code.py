import requests
import numpy as np
from haversine import haversine
from datetime import datetime
from pytz import timezone

def getGeoCode(address, client_id,client_secret):
    header = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    endpoint = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    url = f"{endpoint}?query={address}"
    res=requests.get(url,headers=header)
    return res

def get_bus_station(citycode,bus_station) :
  url_bus_station = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getSttnNoList'
  params_bus_station ={'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'pageNo' : '1', 'numOfRows' : '10', '_type' : 'json', 'cityCode' : citycode, 'nodeNm' : bus_station }
  response_bus_station = requests.get(url_bus_station, params=params_bus_station)
  return response_bus_station.json()['response']['body']['items']['item']

def get_bus_arrive(citycode,nodeid) :
  url_bus_arrive = 'http://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList'
  params_bus_arrive ={'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'pageNo' : '1', 'numOfRows' : '20', '_type' : 'json', 'cityCode' : citycode, 'nodeId' : nodeid }
  response_bus_arrive = requests.get(url_bus_arrive, params=params_bus_arrive)
  return response_bus_arrive.json()['response']['body']['items']['item']


home_address = input("출발할 주소를 입력하세요 : ")
start_bus_station = input("출발 버스정류장을 입력하세요 : ")
start_city=input("출발버스정류장의 지역를 입력하세요 : ")
end_bus_station = input("도착 버스정류장을 입력하세요 : ")
end_city=input("도착버스정류장의 지역 입력하세요 : ")
bus_number=input('탑승할 버스번호를 입력하세요 : ')
subway_station=input('탑승할 지하철역 이름을 입력하세요 ("역"제외): ')
margin_minute=int(input('추가시간을 입력하세요(분) : '))

# home_address = "인천광역시 동구 화도진로 187"
# start_bus_station = "만석주공"
# start_city='인천광역시'
# end_bus_station = "동인천역"
# end_city='인천광역시'
# bus_number='506'
# subway_station="동인천"
# margin_minute=2

#home_address = "인천광역시 연수구 아카데미로 119"
#start_bus_station = "인천대정문"
#start_city='인천광역시'
#end_bus_station = "인천대입구역"
#end_city='인천광역시'
#bus_number='16'
#subway_station="인천대입구"
#margin_minute=2

print('=====================================================')
margin_second=margin_minute*60

if __name__=='__main__':
    address1=home_address
    client_id="pb497ugjwe"
    client_secret="34RBuMEwl3rrbVpvQZWgkuQt7STvADuMihiY0n7Y"
    
    response1=getGeoCode(address1,client_id,client_secret)
    
    if(response1.status_code==200):
        result=response1.json()
        x1=float(result['addresses'][0]['x'])
        y1=float(result['addresses'][0]['y'])
    else:
        print(f'Error code:{response1}')

#지역코드 추출
url_citycode = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCtyCodeList'
params_citycode = {'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==','_type' : 'json'}
response_citycode=requests.get(url_citycode,params=params_citycode)
res_citycode=response_citycode.json()['response']['body']['items']['item']
len_citycode=len(res_citycode)
for i in range(len_citycode) :
  if start_city in res_citycode[i]['cityname'] :
    start_citycode=res_citycode[i]['citycode']
  if end_city in res_citycode[i]['cityname'] :
    end_citycode=res_citycode[i]['citycode']

#버스정류소정보(출발버스정류장)
res_bus_station=get_bus_station(start_citycode,start_bus_station)
num=0
bus_station_dict={}

if type(res_bus_station) == type({}) :
  bus_station_dict[0] = res_bus_station

elif type(res_bus_station) == type([]) :
  for i in range(len(res_bus_station)) :
    print(f"{i} -> {res_bus_station[i]['nodenm']} : {res_bus_station[i]['nodeno']}")
  num=int(input("출발버스정류장을 선택하세요 : "))
  bus_station_dict[0] = res_bus_station[num]
  print('=====================================================')

#버스정류소정보(도착버스정류장)
res_bus_station=get_bus_station(end_citycode,end_bus_station)
num=0

if type(res_bus_station) == type({}) :
  bus_station_dict[1] = res_bus_station

elif type(res_bus_station) == type([]) :
  for i in range(len(res_bus_station)) :
    print(f"{i} -> {res_bus_station[i]['nodenm']} : {res_bus_station[i]['nodeno']}")
  num=int(input("도착버스정류장을 선택하세요 : "))
  bus_station_dict[1] = res_bus_station[num]
  print('=====================================================')

#버스도착정보(출발버정)
res_bus_arrive=get_bus_arrive(start_citycode,bus_station_dict[0]['nodeid'])
start_bus_dict={}
cnt=0

for i in range(len(res_bus_arrive)) :
  if str(res_bus_arrive[i]['routeno'])==str(bus_number) :
    start_bus_dict[cnt]={
      'arrtime' : res_bus_arrive[i]['arrtime'],
      'arrcnt'  : res_bus_arrive[i]['arrprevstationcnt']
    }
    cnt=cnt+1

#버스도착정보(도착버정)
res_bus_arrive=get_bus_arrive(end_citycode,bus_station_dict[1]['nodeid'])
end_bus_dict={}

cnt=0
for i in range(len(res_bus_arrive)) :
  if str(res_bus_arrive[i]['routeno'])==str(bus_number) :
    end_bus_dict[cnt]={
      'arrtime' : res_bus_arrive[i]['arrtime'],
      'arrcnt'  : res_bus_arrive[i]['arrprevstationcnt']
    }
    cnt=cnt+1

now =datetime.now(timezone('Asia/Seoul'))

x2=float(bus_station_dict[0]['gpslong'])
y2=float(bus_station_dict[0]['gpslati'])

pos1=(y1,x1)
pos2=(y2,x2)

d=haversine(pos1, pos2) * 1000 # 출발위치와 도착위치 거리(미터)
time=int(np.floor(d/67))
hour=time//60 # 시간
minute=time%60+margin_minute# 분
second=time*60+margin_second

start_arrtime=999999
end_arrtime=999999

for i in range(len(start_bus_dict)):
  if start_bus_dict[i]['arrtime']> second :
    start_arrtime= start_bus_dict[i]['arrtime']
    start_arrcnt=start_bus_dict[i]['arrcnt']
  
if start_arrtime==999999 :
  print("버스도착정보 및 시간안에 탈 수 있는 버스가 없습니다.")
  exit()

else :
  cnt=0
  for i in range(len(end_bus_dict)) : 
    if end_bus_dict[i]['arrcnt'] < start_arrcnt :
      pass
    else :
      end_arrtime=end_bus_dict[i]['arrtime']
      end_arrcnt=end_bus_dict[i]['arrcnt']
      break

if end_arrtime == 999999 :
    print("버스도착정보 및 시간안에 탈 수 있는 버스가 없습니다.")
    exit()


start_arrtime=int(np.floor(start_arrtime/60))
end_arrtime=int(np.floor(end_arrtime/60))

arr_hour = now.hour
arr_minute=now.minute+start_arrtime-minute

dpt_hour = now.hour
dpt_minute=now.minute+end_arrtime

if arr_minute >=60:
  arr_hour = arr_hour + 1
  arr_minute = arr_minute%60
  
if arr_hour >=24:
  arr_hour=arr_hour%24

if dpt_minute >=60:
  dpt_hour = dpt_hour + 1
  dpt_minute = dpt_minute%60
  
if dpt_hour >=24:
  dpt_hour=dpt_hour%24

print(f'start_arrtime = {start_arrtime}, end_arrtime = {end_arrtime}' )
print("")
print(f"현재시간 : {now.hour}시 {now.minute}분")
print("")
print(f"출발시간 : {arr_hour}시 {arr_minute}분")
print("")
print(f"도착시간 : {dpt_hour}시 {dpt_minute}분")

cnt = 1

change_station_dict = {}  

#지하철 이름 검색하면 지하철 id 찾아주는 부분

station_name = subway_station
print(station_name)

print("상행과 하행을 선택하세요. 상행은 U, 하행은 D")
Choose_line = input()

url = 'http://apis.data.go.kr/1613000/SubwayInfoService/getKwrdFndSubwaySttnList'
params_subway_station_id = {'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'numOfRows' : '10', 'pageNo' : '1', '_type' : 'json', 'subwayStationName' : station_name}
response_subway_station_id= requests.get(url, params=params_subway_station_id)
res_subway_arrive_id = response_subway_station_id.json() #환승역이 있는지 없는지 먼저 판별해 보기 위해 request 보내는 곳


if type(res_subway_arrive_id['response']['body']['items']['item']) == type([]): # 환승역 처리
    print("환승역입니다.")
    print('')

    count = len(res_subway_arrive_id['response']['body']['items']['item'])
    
    for n in range(0,count):
        change_station_dict[n] = res_subway_arrive_id['response']['body']['items']['item'][n]['subwayStationId'] # 호선 선택을 위해 dict 에 저장
        print(res_subway_arrive_id['response']['body']['items']['item'][n]['subwayStationName'])
        print(res_subway_arrive_id['response']['body']['items']['item'][n]['subwayStationId'])
        print(res_subway_arrive_id['response']['body']['items']['item'][n]['subwayRouteName'])
        print('=====================================================')

    print(change_station_dict)
    print("몇호선을 선택하시겠습니까?")
    choose = int(input()) # 0 or 1 
    print(change_station_dict[choose])

    #위에서 선택한 station_id 를 토대로 다시 요청해서 받아오는 부분
    url1 = 'http://apis.data.go.kr/1613000/SubwayInfoService/getSubwaySttnAcctoSchdulList'
    params_subway_arrive_time ={'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'pageNo' : cnt, 'numOfRows' : '1', '_type' : 'json', 'subwayStationId' : change_station_dict[choose], 'dailyTypeCode' : '01','upDownTypeCode' : Choose_line} #U는 상행선
    response_subway_arrive_time1= requests.get(url1, params=params_subway_arrive_time)
    res_subway_arrive_time1 = response_subway_arrive_time1.json()


    #맨처음 시간
    print(res_subway_arrive_time1['response']['body']['items']['item']['subwayStationNm'])
    arrive_time_list1 = [] 
    arrive_time_list1.append(res_subway_arrive_time1['response']['body']['items']['item']['arrTime'])

    totalcount_len = res_subway_arrive_time1['response']['body']['totalCount'] #시간표가 총 몇개인지 구하는 것
    print(totalcount_len)

    for cnt in range(2,totalcount_len): #도착시간들 list 에 저장
        params_subway_arrive_time ={'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'pageNo' : cnt, 'numOfRows' : '1', '_type' : 'json', 'subwayStationId' : change_station_dict[choose], 'dailyTypeCode' : '01','upDownTypeCode' : Choose_line} #U는 상행선
        response_subway_arrive_time= requests.get(url1, params=params_subway_arrive_time)
        res_subway_arrive_time = response_subway_arrive_time.json()
        arrive_time_list1.append(res_subway_arrive_time['response']['body']['items']['item']['arrTime'])
       
    print(arrive_time_list1)
    arrive_time_list_len = len(arrive_time_list1)

    print('=====================================================')

    dpt_minute=str(dpt_minute)
    if len(dpt_minute) == 1:
        dpt_minute='0'+dpt_minute
    a = int(str(dpt_hour)+dpt_minute+'00')

    print("===============입력된 시간 이후의 시간표===============")

    cnt2 = 0

    for i in range(0,int(arrive_time_list_len)):
        if int(arrive_time_list1[i]) > int(a):
            print(f'HHMMSS : {arrive_time_list1[i]}')
            cnt2 = cnt2+1
        if cnt2 > 1 :
            break
    
#환승역이 아닌 단일 정거장이면,
elif type(res_subway_arrive_id['response']['body']['items']['item'])== type({}): 
    print('환승역이 없습니다.')

    url1 = 'http://apis.data.go.kr/1613000/SubwayInfoService/getSubwaySttnAcctoSchdulList'
    params_subway_arrive_time ={'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'pageNo' : cnt, 'numOfRows' : '1', '_type' : 'json', 'subwayStationId' : res_subway_arrive_id['response']['body']['items']['item']['subwayStationId'], 'dailyTypeCode' : '01','upDownTypeCode' : Choose_line} #U는 상행선
    response_subway_arrive_time1= requests.get(url1, params=params_subway_arrive_time)
    res_subway_arrive_time1 = response_subway_arrive_time1.json()

    totalcount_len= res_subway_arrive_time1['response']['body']['totalCount']

    arrive_time_list2 = []
    arrive_time_list2.append(res_subway_arrive_time1['response']['body']['items']['item']['arrTime'])


    for cnt in range(2,totalcount_len):
        params_subway_arrive_time ={'serviceKey' : 'bf45zbmfccdE+q0rEY+zAi+sTICjy/0GStubXVsA11Mm0Q0ite1NXnyoZU9tRK8ov5dRUT7iMoLMd12YinibNQ==', 'pageNo' : cnt, 'numOfRows' : '1', '_type' : 'json', 'subwayStationId' : res_subway_arrive_id['response']['body']['items']['item']['subwayStationId'], 'dailyTypeCode' : '01','upDownTypeCode' : Choose_line} #U는 상행선
        response_subway_arrive_time= requests.get(url1, params=params_subway_arrive_time)
        res_subway_arrive_time = response_subway_arrive_time.json()
        arrive_time_list2.append(res_subway_arrive_time['response']['body']['items']['item']['arrTime']) #가져온 시간을 리스트에 저장

    arrive_time_list_len = len(arrive_time_list2)

    dpt_minute=str(dpt_minute)
    if len(dpt_minute) == 1:
        dpt_minute='0'+dpt_minute
    a = int(str(dpt_hour)+dpt_minute+'00')

    print("===============예상도착 시간 이후의 다음 열차 시간표===============")

    cnt2 = 0

    for i in range(0,arrive_time_list_len):
        if int(arrive_time_list2[i]) > a:
            print(f'HHMMSS : {arrive_time_list2[i]}')
            cnt2 = cnt2+1
        if cnt2 > 1:
            break
    
