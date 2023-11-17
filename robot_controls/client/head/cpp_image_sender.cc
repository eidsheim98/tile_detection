/**
    C++ client that runs on the Unitree Go1 Edu head unit
    Takes pictures using the Unitree Camera SDK, and sends it to the python server
  */

#include <UnitreeCameraSDK.hpp>
#include <unistd.h>
#include <iostream>
#include <unistd.h>

#include <iostream>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char *argv[]){

    int deviceNode = 0; ///< default 0 -> /dev/video0
    cv::Size frameSize(1856, 800); ///< default frame size 1856x800
    int fps = 30; ///< default camera fps: 30

    if(argc >= 2){
        deviceNode = std::atoi(argv[1]);
        if(argc >= 4){
            frameSize = cv::Size(std::atoi(argv[2]), std::atoi(argv[3]));
        }
        if(argc >=5)
            fps = std::atoi(argv[4]);
    }

    UnitreeCamera cam(deviceNode); ///< init camera by device node number
    if(!cam.isOpened())   ///< get camera open state
        exit(EXIT_FAILURE);

    cam.setRawFrameSize(frameSize); ///< set camera frame size
    cam.setRawFrameRate(fps);       ///< set camera camera fps
    cam.setRectFrameSize(cv::Size(frameSize.width >> 2, frameSize.height >> 1)); ///< set camera rectify frame size
    cam.startCapture(); ///< disable image h264 encoding and share memory sharing

    int sock = 0, valread;
    struct sockaddr_in serv_addr;


    // Create socket
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(8887);
    serv_addr.sin_addr.s_addr = inet_addr("192.168.12.134");

    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        printf("\n Socket creation error \n");
        return -1;
    }


    usleep(500000);
    while(cam.isOpened()){
        cv::Mat left,right,feim;
        if(!cam.getRectStereoFrame(left,right,feim)){ ///< get longlat rectify left,right and fisheye rectify feim
            usleep(1000);
            continue;
        }

    std::vector<uchar> buf;
    cv::imencode(".jpg",feim,buf);

    const char *data = reinterpret_cast<char*>(buf.data());

    int strLength = buf.size();

    std::string strSizeTmp = std::to_string(strLength);
    strSizeTmp = std::string(16-strSizeTmp.length(),'0')+strSizeTmp ;
    char strSize[strSizeTmp.length()+1];
    strcpy(strSize, strSizeTmp.c_str());

    //Send image size and image data
    sendto(sock, (const char *)strSize, 16,
        MSG_CONFIRM, (const struct sockaddr *) &serv_addr,
            sizeof(serv_addr));
    sendto(sock, (const char *)data, strLength,
        MSG_CONFIRM, (const struct sockaddr *) &serv_addr,
            sizeof(serv_addr));

        char key = cv::waitKey(10);
        if(key == 27) // press ESC key
           break;
    }

    cam.stopCapture(); ///< stop camera capturing

    return 0;
}
