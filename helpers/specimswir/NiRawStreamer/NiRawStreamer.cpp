#include "stdafx.h"
#include <WinSock2.h>
#include <Windows.h>

#define _NIWIN  
#include "niimaq.h"

//Private export... http://forums.ni.com/t5/Machine-Vision/Using-NI-IMAQ-imgSnap-ANSI-C-with-Windows-7-x64/m-p/1078765
USER_FUNC  niimaquDisable32bitPhysMemLimitEnforcement(SESSION_ID boardid);

char* intfName;
const int RoiWidth = 320;
const int RoiHeight = 256;
const int RoiLeft = 0;
const int RoiTop = 0;

// error checking macro
#define errChk(fCall) if (ImaqError = (fCall), ImaqError < 0) {goto End;} else

bool CaptureAndSend(SOCKET s) {
	int frame = 0;
	IMG_ERR ImaqError = 0;
	INTERFACE_ID Iid;
	SESSION_ID Sid;
	uInt32 bufferSize;
	SHORT abort;
	void *ImaqBuffer = NULL;
	
	// Open an interface and a session
	errChk(imgInterfaceOpen(intfName, &Iid));
	errChk(imgSessionOpen(Iid, &Sid));

	//Disable 64 bits check
	errChk(niimaquDisable32bitPhysMemLimitEnforcement(Sid));

	//Set Region Of Interest
	errChk(imgSetAttribute2(Sid, IMG_ATTR_ROI_WIDTH, RoiWidth));
	errChk(imgSetAttribute2(Sid, IMG_ATTR_ROI_HEIGHT, RoiHeight));
	errChk(imgSetAttribute2(Sid, IMG_ATTR_ROI_LEFT, RoiLeft));
	errChk(imgSetAttribute2(Sid, IMG_ATTR_ROI_TOP, RoiTop));
	errChk(imgSetAttribute2(Sid, IMG_ATTR_ROWPIXELS, RoiWidth));

	errChk(imgSessionGetBufferSize(Sid, &bufferSize));

	//Launch the grabber
	errChk(imgGrabSetup(Sid, TRUE));

	while (!(abort = GetAsyncKeyState(VK_ESCAPE))) {
		errChk(imgGrab(Sid, &ImaqBuffer, TRUE));

		if (send(s, (const char*)&bufferSize, sizeof(uInt32), 0) < 0) {
			printf("send failed!\n");
			break;
		}

		if (send(s, (const char*)ImaqBuffer, bufferSize, 0) < 0) {
			printf("send failed!\n");
			break;
		}
	}

End:
	if (ImaqError < 0) {
		static Int8 ErrorMessage[256];

		memset(ErrorMessage, 0x00, sizeof(ErrorMessage));

		// converts error code to a message
		imgShowError(ImaqError, ErrorMessage);

		printf("%s\n", ErrorMessage);
	}

	// Stop the acquisition
	imgSessionStopAcquisition(Sid);

	// Close the interface and the session
	if (Sid != 0) imgClose(Sid, TRUE);
	if (Iid != 0) imgClose(Iid, TRUE);

	if (abort) {
		return true;
	}
	else {
		return false;
	}
}

//int _tmain(int argc, _TCHAR* argv[])
int main(int argc, char* argv[])
{

	WSAData wsa;
	bool abort;
	char* ip;
	int port;

	if (argc < 4) {
		printf("Usage: %s [interface] [ip] [port]\n", argv[0]);
		return 1;
	}

	intfName = (char*)(argv[1]);
	ip = (char*) (argv[2]);
	port = atoi((char*) (argv[3]));

	printf("Target: %s:%d\n", ip, port);

	if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
		printf("WSAStartup failed, error code=%d\n", WSAGetLastError());
		return 1;
	}

	do {
		SOCKET s;
		struct sockaddr_in target;

		//Create a socket
		if ((s = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET)
		{
			printf("Could not create socket : %d", WSAGetLastError());
			break;
		}

		target.sin_family = AF_INET;
		target.sin_addr.s_addr = inet_addr(ip);
		target.sin_port = htons(port);

		//Connect to remote server
		if (connect(s, (struct sockaddr *)&target, sizeof(target)) < 0)
		{
			printf("connect error\n");
			Sleep(1000);
			continue;
		}

		printf("Press escape to abort...\n\n");
		abort = CaptureAndSend(s);
		printf("Done!\n");
		shutdown(s, SD_SEND);
		closesocket(s);
		
	} while (!abort);

	

	return 0;
}

