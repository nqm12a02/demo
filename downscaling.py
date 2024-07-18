import gdal
import numpy as np

# Định nghĩa các hàm
# Hàm mở file và gán vào một đối tượng thuộc lớp gdal
def openRaster(fn, access):
    ds = gdal.Open(fn, access)
    if ds is None:
        print("Error opening raster dataset")
    return ds

#load một ban từ file đối tượng thuộc lớp gdal là ds. 
#ds được tạo ra bằng cách gọi hàm gdal.Open()    
#kết quả trả lại của hàm là một array trong thư viện numpy (band) đặc trưng cho một lớp độ cao
def getRasterBand(fn, band = 1, access = 0):
    ds = openRaster(fn, access)
    band = ds.GetRasterBand(1).ReadAsArray()
    return band    

#Khởi tạo dữ liệu downscaling, 
#giá trị độ cao ban đầu của các sub-pixel đúng bằng giá trị độ cao của pixel gốc    
def initialize(data, zoom):
    band = np.repeat(data, zoom, axis = 0)
    band = np.repeat(band, zoom, axis = 1)
#    for i in range(0, band.shape[0]):
#        for j in range(0, band.shape[1]):
#            print(band[i][j])
    return band
    
#Tính giá trị của hàm spatial dependence maximisation
def sd(dtin):
  
    width = dtin.shape[0]
    height = dtin.shape[1]
    usd = np.zeros((width, height))
    print(width, height)

    for i in range(0, width):
        for j in range(0, height):
            #set window
            count = 0
            sum = 0.0
            if i == 0:
                swr = 0
            else:
                swr = i - 1
                
            if i == width - 1:
                ewr = i + 1
            else:
                ewr = i + 2
                
            if j == 0:
                swc = 0
            else:
                swc = j - 1
            if j == height - 1:
                ewc = j + 1
            else:
                ewc = j + 2
            for l in range(swr, ewr):
                for m in range(swc, ewc):
                    count += 1
                    sum += dtin[l][m]
            v_current = dtin[i][j]
            vexp = (sum - v_current)/(count - 1)       
            usd[i][j] = vexp - v_current
 
    return usd

#Điều kiện ràng buộc về độ cao, Elevation Function
def elc(dtin, goc):

# Xác định kích thước của DEM gốc và DEM được downscaled  
    width = dtin.shape[0]
    height = dtin.shape[1]
    goc_w = goc.shape[0]
    goc_h = goc.shape[1]
    zoom = int(width/goc_w)
    uec = np.zeros((width, height))
    print(width, height, zoom)
    
    for i in range(0, goc_w):
        for j in range(0, goc_h):
            #determine the average elevation
            #Determine the range of a pixel in the original DEM
            sum = 0.0
            swr = i*zoom
            ewr = swr + zoom
            swc = j*zoom
            ewc = swc + zoom
# Tính tổng của các điểm độ cao của các sub-pixel trên một pixel            
            for l in range(swr, ewr):
                for m in range(swc, ewc):
                    sum += dtin[l][m]
# Độ cao gốc Elevation để tính du_elevation của một pixel gốc
            elev = goc[i][j]
# Độ cao trung bình            
            velc = sum /(zoom*zoom)
# Tính giá trị hiệu chỉnh của hàm độ cao cho từng sub-pixel
            for l in range(swr, ewr):
                for m in range(swc, ewc):
                    uec[l][m] = elev - velc
 
    return uec
    
#Ghi kết quả ra file 
def createRaster(fn, data, driverFmt = "GTiff"):
    driver = gdal.GetDriverByName(driverFmt)
    outds = driver.Create(fn, xsize = data.shape[1], ysize = data.shape[0], bands = 1, eType = gdal.GDT_Float32)
    outds.GetRasterBand(1).WriteArray(data)
    outds = None

# tạo đối tượng str là fn1 chỉ đến file độ cao
fn1 = "D:/Minh/TruongMo/Detaikhoahoc/2020/De tai Bo 2021/PT/ned10m_cut.tif" 
fnout1 = "D:/Minh/TruongMo/Detaikhoahoc/2020/De tai Bo 2021/PT/test1.tif"
fnout2 = "D:/Minh/TruongMo/Detaikhoahoc/2020/De tai Bo 2021/PT/test2.tif"
goc = getRasterBand(fn1)

z = 4 #zoom factor = 4
dscal = initialize(goc, z) #khởi tạo bằng giá trị DEM gốc, OK
Energy_old = 100000000000.0
Threshold = 0.001
Energy_dif = 100000000.0
while abs(Energy_dif) > Threshold:
    usd = sd(dscal)
    uec = elc(dscal, goc)
    u = usd + uec
    Energy_new = abs(usd).sum()+abs(uec).sum()
    dscal = dscal + u
    Energy_dif = Energy_old - Energy_new
    Energy_old = Energy_new
    print(goc.shape, dscal.shape, usd.shape, uec.shape, Energy_new)
    
createRaster(fnout1, dscal)
createRaster(fn1, goc)

iface.addRasterLayer(fnout1)
iface.addRasterLayer(fn1)
#iface.addRasterLayer(fn1)