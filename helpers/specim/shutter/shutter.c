/* shutter.c

   Simple program to control the shutter.
   
   Compilation: gcc -lftdi -o shutter shutter.c && sudo chown root:root shutter && sudo chmod +s shutter
*/

#include <stdio.h>
#include <stdlib.h>
#include <ftdi.h>
#include <unistd.h>

struct ftdi_context *ftdi;

int W(char byte) {
	int ret;
	char bytes[4];
	unsigned char pins;
	
	bytes[0]=byte;
	bytes[1]=byte;
	bytes[2]=byte;
	bytes[3]=byte;
	
	if ((ret = ftdi_write_data(ftdi, bytes, 0x04)) < 0) {
		fprintf(stderr, "unable to write: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
		ftdi_free(ftdi);
        return EXIT_FAILURE;
	}
	
	do {
		ftdi_read_pins(ftdi, &pins);
		//printf("pins=%x, byte=%x\n", pins, byte);
	} while((pins & 0xF) != byte);
	
	usleep(100000);
	return EXIT_SUCCESS;
}


int main(int argc, char *argv[])
{
    int ret;
    unsigned char pins;
    
    //SetUID
    setreuid(geteuid(), getuid());
    
    if ((ftdi = ftdi_new()) == 0)
   {
        fprintf(stderr, "ftdi_new failed\n");
        return EXIT_FAILURE;
    }

    if ((ret = ftdi_usb_open(ftdi, 0x0403, 0x6010)) < 0)
    {
        fprintf(stderr, "unable to open ftdi device: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        return EXIT_FAILURE;
    }
    
    if ((ret = ftdi_set_interface(ftdi, INTERFACE_A)) < 0)
    {
        fprintf(stderr, "unable to set interface: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        return EXIT_FAILURE;
    }
    
    if ((ret = ftdi_set_bitmode(ftdi, 0, 0)) < 0) {
		fprintf(stderr, "unable to set bit mode 1: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
		ftdi_free(ftdi);
        return EXIT_FAILURE;
	}
	
    if ((ret = ftdi_set_bitmode(ftdi, 0x0f, 0x01)) < 0) {
		fprintf(stderr, "unable to set bit mode 2: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
		ftdi_free(ftdi);
        return EXIT_FAILURE;
	}
	
	ret = 0;
	
	//Initialization
	if (argc == 1) {
		ret = 1;
		W(0x0F); W(0x07); W(0x0F); W(0x07); W(0x0F); W(0x0C); W(0x0E); W(0x0F);
	} else if (argc == 2) {
		if (strncmp("1", argv[1], 1) == 0) {
			ret = 1;
			//Open shutter
			W(0x07); W(0x0F); W(0x0C); W(0x0E); W(0x0F);
		} else if (strncmp("0", argv[1], 1) == 0) {
			ret = 1;
			//Close shutter
			W(0x07); W(0x0F); W(0x0A); W(0x0E); W(0x0F);
		}
	}
	
	if (!ret) {
		fprintf(stderr, "Usage: %s {0|1}\n", argv[0]);
	}
	
    if ((ret = ftdi_usb_close(ftdi)) < 0)
    {
        fprintf(stderr, "unable to close ftdi device: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        return EXIT_FAILURE;
    }

    ftdi_free(ftdi);

    return EXIT_SUCCESS;
}
