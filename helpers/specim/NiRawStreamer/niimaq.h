//////////////////////////////////////////////////////////////////////////////
//
//  Title     : niimaq.h
//  Project   : NI-IMAQ
//  Created   : 1/18/2002 @ 15:16:23
//  Platforms : All
//  Copyright : National Instruments 2007.  All Rights Reserved.
//  Access    : Public
//  Purpose   : Public header file for NI-IMAQ.
//
//////////////////////////////////////////////////////////////////////////////


//============================================================================
//  Preamble
//============================================================================
#if !defined(niimaq_h)
#define niimaq_h


//============================================================================
//  Pragmas
//============================================================================
#ifdef _CVI_
    #pragma  EnableLibraryRuntimeChecking
#endif


//============================================================================
//  Typedefs
//============================================================================
#if !defined(niimaq_types)
#define niimaq_types

#ifndef _NI_uInt8_DEFINED_
    #define _NI_uInt8_DEFINED_
    typedef unsigned char       uInt8;
#endif

#ifndef _NI_uInt16_DEFINED_
    #define _NI_uInt16_DEFINED_
    typedef unsigned short int  uInt16;
#endif

#ifndef _NI_uInt32_DEFINED_
    #define _NI_uInt32_DEFINED_
    typedef unsigned long       uInt32;
#endif

#ifndef _NI_uInt64_DEFINED_
    #if defined(_MSC_VER) || _CVI_ >= 700
        #define _NI_uInt64_DEFINED_
        typedef unsigned __int64   uInt64;
    #elif defined(__GNUC__)
        #define _NI_uInt64_DEFINED_
        typedef unsigned long long uInt64;
    #endif
#endif

#ifndef _NI_Int8_DEFINED_
    #define _NI_Int8_DEFINED_
    typedef char                Int8;
#endif

#ifndef _NI_Int16_DEFINED_
    #define _NI_Int16_DEFINED_
    typedef short int           Int16;
#endif

#ifndef _NI_Int32_DEFINED_
    #define _NI_Int32_DEFINED_
    typedef long                Int32;
#endif

#ifndef _NI_Int64_DEFINED_
    #if defined(_MSC_VER) || _CVI_ >= 700
        #define _NI_Int64_DEFINED_
        typedef __int64         Int64;
    #elif defined(__GNUC__)
        #define _NI_Int64_DEFINED_
        typedef long long       Int64;
    #endif
#endif

#ifndef TRUE
    #define TRUE                1
#endif

#ifndef FALSE
    #define FALSE               0
#endif

typedef char*           Ptr;

typedef  uInt32   INTERFACE_ID;
typedef  uInt32   SESSION_ID;
typedef  uInt32   EVENT_ID;
typedef  uInt32   PULSE_ID;
typedef  uInt32   BUFLIST_ID;
typedef  Int32    IMG_ERR;
typedef  uInt16   IMG_SYNC;
typedef  uInt32   GUIHNDL;

#endif


//============================================================================
//  Includes
//============================================================================
#include <stddef.h>


//============================================================================
//  Defines
//============================================================================
#if (defined(__cplusplus) || defined(__cplusplus__))
    #define USER_EXTERN_C extern "C"
#else
    #define USER_EXTERN_C
#endif

#if defined(_MSC_VER)
    #ifndef NI_DLL_IMPORT
        #define NI_DLL_IMPORT __declspec(dllimport)
    #endif
    #ifndef NI_DLL_EXPORT
        #define NI_DLL_EXPORT __declspec(dllexport)
    #endif
    #ifndef NI_STDCALL
        #define NI_STDCALL    __stdcall
    #endif
    #ifndef NI_CDECL
        #define NI_CDECL      __cdecl
    #endif
#elif (defined(_CVI_) || defined(_CVI))
    #ifndef NI_DLL_IMPORT
        #define NI_DLL_IMPORT
    #endif
    #ifndef NI_DLL_EXPORT
        #define NI_DLL_EXPORT __declspec(dllexport)
    #endif
    #ifndef NI_STDCALL
        #define NI_STDCALL    __stdcall
    #endif
    #ifndef NI_CDECL
        #define NI_CDECL      __cdecl
    #endif
#elif defined(__GNUC__)
    #ifndef NI_DLL_IMPORT
        #define NI_DLL_IMPORT
    #endif
    #ifndef NI_DLL_EXPORT
        #define NI_DLL_EXPORT __attribute__ ((section (".export")))
    #endif
    #ifndef NI_STDCALL
        #define NI_STDCALL
    #endif
    #ifndef NI_CDECL
        #define NI_CDECL
    #endif
#endif

#if !defined(USER_MODE_BUILD)
    #define USER_FUNC USER_EXTERN_C NI_DLL_IMPORT Int32 NI_STDCALL
    #define USER_FUNCC USER_EXTERN_C NI_DLL_IMPORT Int32 NI_CDECL
#else
    #define USER_FUNC USER_EXTERN_C NI_DLL_EXPORT Int32 NI_STDCALL
    #define USER_FUNCC USER_EXTERN_C NI_DLL_EXPORT Int32 NI_CDECL
#endif

#define _IMG_BASE 0x3FF60000


//----------------------------------------------------------------------------
//  Attribute Keys
//----------------------------------------------------------------------------
#define  IMG_ATTR_INTERFACE_TYPE                (_IMG_BASE + 0x0001) // id of board - see constants below
#define  IMG_ATTR_PIXDEPTH                      (_IMG_BASE + 0x0002) // pixel depth in bits
#define  IMG_ATTR_COLOR                         (_IMG_BASE + 0x0003) // true = supports color
#define  IMG_ATTR_HASRAM                        (_IMG_BASE + 0x0004) // true = has on-board SRAM
#define  IMG_ATTR_RAMSIZE                       (_IMG_BASE + 0x0005) // SRAM size
#define  IMG_ATTR_CHANNEL                       (_IMG_BASE + 0x0006)
#define  IMG_ATTR_FRAME_FIELD                   (_IMG_BASE + 0x0007) // supports frame and field
#define  IMG_ATTR_HORZ_RESOLUTION               (_IMG_BASE + 0x0009)
#define  IMG_ATTR_VERT_RESOLUTION               (_IMG_BASE + 0x000A)
#define  IMG_ATTR_LUT                           (_IMG_BASE + 0x000B)
#define  IMG_ATTR_LINESCAN                      (_IMG_BASE + 0x000C)
#define  IMG_ATTR_GAIN                          (_IMG_BASE + 0x000D)
#define  IMG_ATTR_CHROMA_FILTER                 (_IMG_BASE + 0x000E)
#define  IMG_ATTR_WHITE_REF                     (_IMG_BASE + 0x000F)
#define  IMG_ATTR_BLACK_REF                     (_IMG_BASE + 0x0010)
#define  IMG_ATTR_DATALINES                     (_IMG_BASE + 0x0011) // pass in uInt32 array of size up to 16 elements to swap incoming data lines (0,1,2...15) - must be 16 x uInt32 array
#define  IMG_ATTR_NUM_EXT_LINES                 (_IMG_BASE + 0x0012)
#define  IMG_ATTR_NUM_RTSI_LINES                (_IMG_BASE + 0x0013)
#define  IMG_ATTR_NUM_RTSI_IN_USE               (_IMG_BASE + 0x0014)
#define  IMG_ATTR_MEM_LOCKED                    (_IMG_BASE + 0x0065)
#define  IMG_ATTR_BITSPERPIXEL                  (_IMG_BASE + 0x0066)
#define  IMG_ATTR_BYTESPERPIXEL                 (_IMG_BASE + 0x0067)
#define  IMG_ATTR_ACQWINDOW_LEFT                (_IMG_BASE + 0x0068)
#define  IMG_ATTR_ACQWINDOW_TOP                 (_IMG_BASE + 0x0069)
#define  IMG_ATTR_ACQWINDOW_WIDTH               (_IMG_BASE + 0x006A)
#define  IMG_ATTR_ACQWINDOW_HEIGHT              (_IMG_BASE + 0x006B)
#define  IMG_ATTR_LINE_COUNT                    (_IMG_BASE + 0x0070)
#define  IMG_ATTR_FREE_BUFFERS                  (_IMG_BASE + 0x0071)
#define  IMG_ATTR_HSCALE                        (_IMG_BASE + 0x0072)
#define  IMG_ATTR_VSCALE                        (_IMG_BASE + 0x0073)
#define  IMG_ATTR_ACQ_IN_PROGRESS               (_IMG_BASE + 0x0074)
#define  IMG_ATTR_START_FIELD                   (_IMG_BASE + 0x0075)
#define  IMG_ATTR_FRAME_COUNT                   (_IMG_BASE + 0x0076)
#define  IMG_ATTR_LAST_VALID_BUFFER             (_IMG_BASE + 0x0077)
#define  IMG_ATTR_ROWBYTES                      (_IMG_BASE + 0x0078)
#define  IMG_ATTR_CALLBACK                      (_IMG_BASE + 0x007B)
#define  IMG_ATTR_CURRENT_BUFLIST               (_IMG_BASE + 0x007C)
#define  IMG_ATTR_FRAMEWAIT_MSEC                (_IMG_BASE + 0x007D)
#define  IMG_ATTR_TRIGGER_MODE                  (_IMG_BASE + 0x007E)
#define  IMG_ATTR_INVERT                        (_IMG_BASE + 0x0082)
#define  IMG_ATTR_XOFF_BUFFER                   (_IMG_BASE + 0x0083)
#define  IMG_ATTR_YOFF_BUFFER                   (_IMG_BASE + 0x0084)
#define  IMG_ATTR_NUM_BUFFERS                   (_IMG_BASE + 0x0085)
#define  IMG_ATTR_LOST_FRAMES                   (_IMG_BASE + 0x0088)
#define  IMG_ATTR_COLOR_WHITE_REF               (_IMG_BASE + 0x008F) // Color white reference
#define  IMG_ATTR_COLOR_BLACK_REF               (_IMG_BASE + 0x0090) // Color black reference
#define  IMG_ATTR_COLOR_CLAMP_START             (_IMG_BASE + 0x0091) // Color clamp start
#define  IMG_ATTR_COLOR_CLAMP_STOP              (_IMG_BASE + 0x0092) // Color clamp stop
#define  IMG_ATTR_COLOR_ZERO_START              (_IMG_BASE + 0x0093) // Color zero start
#define  IMG_ATTR_COLOR_ZERO_STOP               (_IMG_BASE + 0x0094) // Color zero stop
#define  IMG_ATTR_COLOR_AVG_COUNT               (_IMG_BASE + 0x0095) // Color averaging count
#define  IMG_ATTR_COLOR_SW_CHROMA_FILTER        (_IMG_BASE + 0x0096) // Color SW chroma filter
#define  IMG_ATTR_COLOR_NTSC_SETUP_ENABLE       (_IMG_BASE + 0x0097) // Color NTSC Setup enable
#define  IMG_ATTR_COLOR_NTSC_SETUP_VALUE        (_IMG_BASE + 0x0098) // Color NTSC Setup value
#define  IMG_ATTR_COLOR_BRIGHTNESS              (_IMG_BASE + 0x0099) // Color brightness
#define  IMG_ATTR_COLOR_CONTRAST                (_IMG_BASE + 0x009A) // Color contrast
#define  IMG_ATTR_COLOR_SATURATION              (_IMG_BASE + 0x009B) // Color saturation
#define  IMG_ATTR_COLOR_TINT                    (_IMG_BASE + 0x009C) // Color tint (chroma phase)
#define  IMG_ATTR_COLOR_SW_POST_GAIN            (_IMG_BASE + 0x009D) // Color SW post-gain
#define  IMG_ATTR_COLOR_BURST_START             (_IMG_BASE + 0x009E) // Color burst start
#define  IMG_ATTR_COLOR_BURST_STOP              (_IMG_BASE + 0x009F) // Color burst stop
#define  IMG_ATTR_COLOR_BLANK_START             (_IMG_BASE + 0x00A0) // Color blank start
#define  IMG_ATTR_COLOR_BLANK_STOP              (_IMG_BASE + 0x00A1) // Color blank stop
#define  IMG_ATTR_COLOR_IMAGE_X_SHIFT           (_IMG_BASE + 0x00A2) // Color acquisition left shift
#define  IMG_ATTR_COLOR_GAIN                    (_IMG_BASE + 0x00A3) // Color HW pre-gain
#define  IMG_ATTR_COLOR_CLAMP_START_REF         (_IMG_BASE + 0x00A5) // Color clamp start reference
#define  IMG_ATTR_COLOR_CLAMP_STOP_REF          (_IMG_BASE + 0x00A6) // Color clamp stop reference
#define  IMG_ATTR_COLOR_ZERO_START_REF          (_IMG_BASE + 0x00A7) // Color zero start reference
#define  IMG_ATTR_COLOR_ZERO_STOP_REF           (_IMG_BASE + 0x00A8) // Color zero stop reference
#define  IMG_ATTR_COLOR_BURST_START_REF         (_IMG_BASE + 0x00A9) // Color burst start reference
#define  IMG_ATTR_COLOR_BURST_STOP_REF          (_IMG_BASE + 0x00AA) // Color burst stop reference
#define  IMG_ATTR_COLOR_BLANK_START_REF         (_IMG_BASE + 0x00AB) // Color blank start reference
#define  IMG_ATTR_COLOR_BLANK_STOP_REF          (_IMG_BASE + 0x00AC) // Color blank stop reference
#define  IMG_ATTR_COLOR_MODE                    (_IMG_BASE + 0x00AD) // Color acquisition mode
#define  IMG_ATTR_COLOR_IMAGE_REP               (_IMG_BASE + 0x00AE) // Color Image representation
#define  IMG_ATTR_GENLOCK_SWITCH_CHAN           (_IMG_BASE + 0x00AF) // switch channel fast
#define  IMG_ATTR_CLAMP_START                   (_IMG_BASE + 0x00B0) // clamp start
#define  IMG_ATTR_CLAMP_STOP                    (_IMG_BASE + 0x00B1) // clamp stop
#define  IMG_ATTR_ZERO_START                    (_IMG_BASE + 0x00B2) // zero start
#define  IMG_ATTR_ZERO_STOP                     (_IMG_BASE + 0x00B3) // zero stop
#define  IMG_ATTR_COLOR_HUE_OFFS_ANGLE          (_IMG_BASE + 0x00B5) // Color hue offset angle
#define  IMG_ATTR_COLOR_IMAGE_X_SHIFT_REF       (_IMG_BASE + 0x00B6) // Color acquisition left shift reference
#define  IMG_ATTR_LAST_VALID_FRAME              (_IMG_BASE + 0x00BA) // returns the cummulative buffer index (frame#)
#define  IMG_ATTR_CLOCK_FREQ                    (_IMG_BASE + 0x00BB) // returns the max clock freq of the board
#define  IMG_ATTR_BLACK_REF_VOLT                (_IMG_BASE + 0x00BC) // defines the black reference in volts
#define  IMG_ATTR_WHITE_REF_VOLT                (_IMG_BASE + 0x00BD) // defines the white reference in volts
#define  IMG_ATTR_COLOR_LOW_REF_VOLT            (_IMG_BASE + 0x00BE) // defines the color low reference in volts
#define  IMG_ATTR_COLOR_HIGH_REF_VOLT           (_IMG_BASE + 0x00BF)
#define  IMG_ATTR_GETSERIAL                     (_IMG_BASE + 0x00C0) // get the serial number of the board
#define  IMG_ATTR_ROWPIXELS                     (_IMG_BASE + 0x00C1)
#define  IMG_ATTR_ACQUIRE_FIELD                 (_IMG_BASE + 0x00C2)
#define  IMG_ATTR_PCLK_DETECT                   (_IMG_BASE + 0x00C3)
#define  IMG_ATTR_VHA_MODE                      (_IMG_BASE + 0x00C4) // Variable Height Acquisition mode
#define  IMG_ATTR_BIN_THRESHOLD_LOW             (_IMG_BASE + 0x00C5) // Binary threshold low
#define  IMG_ATTR_BIN_THRESHOLD_HIGH            (_IMG_BASE + 0x00C6) // Binary threshold hi
#define  IMG_ATTR_COLOR_LUMA_BANDWIDTH          (_IMG_BASE + 0x00C7) // selects different bandwidths for the luminance signal
#define  IMG_ATTR_COLOR_CHROMA_TRAP             (_IMG_BASE + 0x00C8) // enables and disables the chroma trap filter in the luma signal path
#define  IMG_ATTR_COLOR_LUMA_COMB               (_IMG_BASE + 0x00C9) // select the type of comb filter used in the luma path
#define  IMG_ATTR_COLOR_PEAKING_ENABLE          (_IMG_BASE + 0x00CA) // enable the peaking filter in the luma path
#define  IMG_ATTR_COLOR_PEAKING_LEVEL           (_IMG_BASE + 0x00CB)
#define  IMG_ATTR_COLOR_CHROMA_PROCESS          (_IMG_BASE + 0x00CC) // specifies the processing applied to the chroma signal
#define  IMG_ATTR_COLOR_CHROMA_BANDWIDTH        (_IMG_BASE + 0x00CD) // bandwidth of the chroma information of the image
#define  IMG_ATTR_COLOR_CHROMA_COMB             (_IMG_BASE + 0x00CE) // select the type of comb filter used in the chroma path
#define  IMG_ATTR_COLOR_CHROMA_PHASE            (_IMG_BASE + 0x00CF) // sets value of correction angle applied to the chroma vector.  Active only for NTSC cameras
#define  IMG_ATTR_COLOR_RGB_CORING_LEVEL        (_IMG_BASE + 0x00D0) // select RGB coring level
#define  IMG_ATTR_COLOR_HSL_CORING_LEVEL        (_IMG_BASE + 0x00D1) // select HSL coring level
#define  IMG_ATTR_COLOR_HUE_REPLACE_VALUE       (_IMG_BASE + 0x00D2) // hue value to replace if saturation value is less than HSL coring level
#define  IMG_ATTR_COLOR_GAIN_RED                (_IMG_BASE + 0x00D3) // Red Gain
#define  IMG_ATTR_COLOR_GAIN_GREEN              (_IMG_BASE + 0x00D4) // Green Gian
#define  IMG_ATTR_COLOR_GAIN_BLUE               (_IMG_BASE + 0x00D5) // Blue Gain
#define  IMG_ATTR_CALIBRATION_DATE_LV           (_IMG_BASE + 0x00D6) // 0 if board is uncalibrated, else seconds since Jan 1 1904
#define  IMG_ATTR_CALIBRATION_DATE              (_IMG_BASE + 0x00D7) // 0 if board is uncalibrated, else seconds since Jan 1 1970
#define  IMG_ATTR_IMAGE_TYPE                    (_IMG_BASE + 0x00D8) // return the IMAQ Vision image type for LabVIEW
#define  IMG_ATTR_DYNAMIC_RANGE                 (_IMG_BASE + 0x00D9) // the effective bits per pixel of the user's white-black level
#define  IMG_ATTR_ACQUIRE_TO_SYSTEM_MEMORY      (_IMG_BASE + 0x011B)
#define  IMG_ATTR_ONBOARD_HOLDING_BUFFER_PTR    (_IMG_BASE + 0x011C) // invalid on 64-bit OS
#define  IMG_ATTR_SYNCHRONICITY                 (_IMG_BASE + 0x011D)
#define  IMG_ATTR_LAST_ACQUIRED_BUFFER_NUM      (_IMG_BASE + 0x011E)
#define  IMG_ATTR_LAST_ACQUIRED_BUFFER_INDEX    (_IMG_BASE + 0x011F)
#define  IMG_ATTR_LAST_TRANSFERRED_BUFFER_NUM   (_IMG_BASE + 0x0120)
#define  IMG_ATTR_LAST_TRANSFERRED_BUFFER_INDEX (_IMG_BASE + 0x0121)
#define  IMG_ATTR_SERIAL_NUM_BYTES_RECEIVED     (_IMG_BASE + 0x012C) // # bytes currently in the internal serial read buffer
#define  IMG_ATTR_EXPOSURE_TIME_INTERNAL        (_IMG_BASE + 0x013C) // exposure time for 1454 (internal value - specified in 40MHz clks)
#define  IMG_ATTR_SERIAL_TERM_STRING            (_IMG_BASE + 0x0150) // The serial termination string
#define  IMG_ATTR_DETECT_VIDEO                  (_IMG_BASE + 0x01A3) // Determines whether to detect a video signal prior to acquiring
#define  IMG_ATTR_ROI_LEFT                      (_IMG_BASE + 0x01A4)
#define  IMG_ATTR_ROI_TOP                       (_IMG_BASE + 0x01A5)
#define  IMG_ATTR_ROI_WIDTH                     (_IMG_BASE + 0x01A6)
#define  IMG_ATTR_ROI_HEIGHT                    (_IMG_BASE + 0x01A7)
#define  IMG_ATTR_NUM_ISO_IN_LINES              (_IMG_BASE + 0x01A8) // The number of iso in lines the device supports
#define  IMG_ATTR_NUM_ISO_OUT_LINES             (_IMG_BASE + 0x01A9) // The number of iso out lines the device supports
#define  IMG_ATTR_NUM_POST_TRIGGER_BUFFERS      (_IMG_BASE + 0x01AA) // The number of buffers that hardware should continue acquire after sensing a stop trigger before it finally does stop
#define  IMG_ATTR_EXT_TRIG_LINE_FILTER          (_IMG_BASE + 0x01AB) // Whether to use filtering on the TTL trigger lines
#define  IMG_ATTR_RTSI_LINE_FILTER              (_IMG_BASE + 0x01AC) // Whether to use filtering on the RTSI trigger lines
#define  IMG_ATTR_NUM_PORTS                     (_IMG_BASE + 0x01AD) // Returns the number of ports that this device supports.
#define  IMG_ATTR_CURRENT_PORT_NUM              (_IMG_BASE + 0x01AE) // Returns the port number that the given interface is using.
#define  IMG_ATTR_ENCODER_PHASE_A_POLARITY      (_IMG_BASE + 0x01AF) // The polarity of the phase A encoder input
#define  IMG_ATTR_ENCODER_PHASE_B_POLARITY      (_IMG_BASE + 0x01B0) // The polarity of the phase B encoder input
#define  IMG_ATTR_ENCODER_FILTER                (_IMG_BASE + 0x01B1) // Specifies whether to use filtering on the encoder input
#define  IMG_ATTR_ENCODER_DIVIDE_FACTOR         (_IMG_BASE + 0x01B2) // The divide factor for the encoder scaler
#define  IMG_ATTR_ENCODER_POSITION              (_IMG_BASE + 0x01B3) // Returns the current value of the absolute encoder position as a uInt64
#define  IMG_ATTR_TEMPERATURE                   (_IMG_BASE + 0x01B4) // The device's current temperature, in degrees C
#define  IMG_ATTR_LED_PASS                      (_IMG_BASE + 0x01B5) // The state of the Pass LED
#define  IMG_ATTR_LED_FAIL                      (_IMG_BASE + 0x01B6) // The state of the Fail LED
#define  IMG_ATTR_SENSOR_PARTIAL_SCAN           (_IMG_BASE + 0x01B7) // The sensor's partial scan mode
#define  IMG_ATTR_SENSOR_BINNING                (_IMG_BASE + 0x01B8) // The sensor's binning mode
#define  IMG_ATTR_SENSOR_GAIN                   (_IMG_BASE + 0x01B9) // The sensor's gain factor
#define  IMG_ATTR_LIGHTING_MODE                 (_IMG_BASE + 0x01BB) // The internal lighting mode to use
#define  IMG_ATTR_LIGHTING_CURRENT              (_IMG_BASE + 0x01BC) // The amount of current sourced by the internal lighting controller (mA)
#define  IMG_ATTR_LIGHTING_MAX_CURRENT          (_IMG_BASE + 0x01BD) // Returns the maximum current that can be souced by the internal lighting controller given the current configuration
#define  IMG_ATTR_LIGHTING_EXT_STROBE_5V_TTL    (_IMG_BASE + 0x01BE) // Whether to enable stobing on the external 5V lighting output
#define  IMG_ATTR_LIGHTING_EXT_STROBE_24V       (_IMG_BASE + 0x01BF) // Whether to enable stobing on the external 24V (VCC) lighting output
#define  IMG_ATTR_SENSOR_EXPOSURE               (_IMG_BASE + 0x01C0) // The sensor's exposure time in milliseconds.
#define  IMG_ATTR_FRAME_RATE                    (_IMG_BASE + 0x01C1) // The frame rate.
#define  IMG_ATTR_MAX_FRAME_RATE                (_IMG_BASE + 0x01C2) // The maximum frame rate.
#define  IMG_ATTR_SEND_SOFTWARE_TRIGGER         (_IMG_BASE + 0x01C3) // Set to issue a software trigger to the action that was configured to wait for a software trigger.
#define  IMG_ATTR_FIXED_FRAME_RATE_MODE         (_IMG_BASE + 0x01C4) // Controls whether the sensor operates in fixed-frame-rate mode (true) or free-run mode (off).  When in fixed-frame-rate mode the sensor will run at the frame rate specified by IMG_ATTR_FRAME_RATE.  When in free-run mode, the sensor will run at the maximum frame rate possible.


//============================================================================
//  Attribute Defines
//============================================================================

//----------------------------------------------------------------------------
//  LUT
//----------------------------------------------------------------------------
#define  IMG_LUT_NORMAL                      0
#define  IMG_LUT_INVERSE                     1
#define  IMG_LUT_LOG                         2
#define  IMG_LUT_INVERSE_LOG                 3
#define  IMG_LUT_BINARY                      4
#define  IMG_LUT_INVERSE_BINARY              5
#define  IMG_LUT_USER                        6


#define  IMG_LUT_TYPE_DEFAULT       0x00000010
#define  IMG_LUT_TYPE_RED           0x00000020
#define  IMG_LUT_TYPE_GREEN         0x00000040
#define  IMG_LUT_TYPE_BLUE          0x00000080
#define  IMG_LUT_TYPE_TAP0          0x00000100
#define  IMG_LUT_TYPE_TAP1          0x00000200
#define  IMG_LUT_TYPE_TAP2          0x00000400
#define  IMG_LUT_TYPE_TAP3          0x00000800


//------------------------------------------------------------------------------
//  Frame or Field Mode
//------------------------------------------------------------------------------
#define  IMG_FIELD_MODE                      0
#define  IMG_FRAME_MODE                      1


//----------------------------------------------------------------------------
//  Chrominance Filters
//----------------------------------------------------------------------------
#define IMG_FILTER_NONE                      0
#define IMG_FILTER_NTSC                      1
#define IMG_FILTER_PAL                       2


//------------------------------------------------------------------------------
//  Possible start field values
//------------------------------------------------------------------------------
#define  IMG_FIELD_EVEN                      0
#define  IMG_FIELD_ODD                       1


//----------------------------------------------------------------------------
//  Scaling
//----------------------------------------------------------------------------
#define  IMG_SCALE_NONE                      1
#define  IMG_SCALE_DIV2                      2
#define  IMG_SCALE_DIV4                      4
#define  IMG_SCALE_DIV8                      8


//----------------------------------------------------------------------------
//  Triggering Mode
//----------------------------------------------------------------------------
#define  IMG_TRIGMODE_NONE                   0
#define  IMG_TRIGMODE_NOREPEAT               1
#define  IMG_TRIGMODE_REPEAT                 2


//----------------------------------------------------------------------------
//  Field Acquisition Selection
//----------------------------------------------------------------------------
#define  IMG_ACQUIRE_EVEN                    0
#define  IMG_ACQUIRE_ODD                     1
#define  IMG_ACQUIRE_ALL                     2
#define  IMG_ACQUIRE_ALTERNATING             3


//----------------------------------------------------------------------------
//  Luma bandwidth
//----------------------------------------------------------------------------
#define  IMG_COLOR_LUMA_BANDWIDTH_FULL       0  // All filters including decimation filter disabled. Default for CCIR or RS-170
#define  IMG_COLOR_LUMA_BANDWIDTH_HIGH       1  // Highest available bandwidth with decimation filter enabled. Default for PAL or NTSC
#define  IMG_COLOR_LUMA_BANDWIDTH_MEDIUM     2  // Decimation filtered enabled, medium bandwidth.
#define  IMG_COLOR_LUMA_BANDWIDTH_LOW        3  // Decimation filtered enabled, lowest bandwidth.


//----------------------------------------------------------------------------
//  Comb filters
//----------------------------------------------------------------------------
#define  IMG_COLOR_COMB_OFF                  0  // Comb filtered disabled (default in S-Video/Y/C mode)
#define  IMG_COLOR_COMB_1LINE                1  // Comb filtered using 1 delayed line
#define  IMG_COLOR_COMB_2LINES               2  // Comb filtered using 2 delayed lines


//----------------------------------------------------------------------------
//  Chroma processing
//----------------------------------------------------------------------------
#define  IMG_COLOR_CHROMA_PROCESS_ALWAYS_OFF 0  // should be used when a monochrome camera is used. Default for RS-170 or CCIR
#define  IMG_COLOR_CHROMA_PROCESS_ALWAYS_ON  1  // should be used when a color camera is used.  Default for NTSC or PAL
#define  IMG_COLOR_CHROMA_PROCESS_AUTODETECT 2  // can be used if the camera type is unknown.


//----------------------------------------------------------------------------
//  Chroma bandwidth
//----------------------------------------------------------------------------
#define  IMG_COLOR_CHROMA_BANDWIDTH_HIGH     0  // Highest bandwidth (default)
#define  IMG_COLOR_CHROMA_BANDWIDTH_LOW      1  // Lowest bandwidth


//----------------------------------------------------------------------------
//  RGB Coring
//----------------------------------------------------------------------------
#define  IMG_COLOR_RGB_CORING_LEVEL_NOCORING 0  // The coring function is disabled
#define  IMG_COLOR_RGB_CORING_LEVEL_C1       1  // Coring activated for saturation equal or below 1 lsb
#define  IMG_COLOR_RGB_CORING_LEVEL_C3       2  // Coring activated for saturation equal or below 3 lsb
#define  IMG_COLOR_RGB_CORING_LEVEL_C7       3  // Coring activated for saturation equal or below 7 lsb


//----------------------------------------------------------------------------
//  Video Signal Types
//----------------------------------------------------------------------------
#define  IMG_VIDEO_NTSC                      0
#define  IMG_VIDEO_PAL                       1


//----------------------------------------------------------------------------
//  imgSessionExamineBuffer constants
//----------------------------------------------------------------------------
#define  IMG_LAST_BUFFER                     0xFFFFFFFE
#define  IMG_OLDEST_BUFFER                   0xFFFFFFFD
#define  IMG_CURRENT_BUFFER                  0xFFFFFFFC


//----------------------------------------------------------------------------
//  Buffer Element Specifiers
//----------------------------------------------------------------------------
#define  IMG_BUFF_ADDRESS                    (_IMG_BASE + 0x007E)
#define  IMG_BUFF_COMMAND                    (_IMG_BASE + 0x007F)
#define  IMG_BUFF_SKIPCOUNT                  (_IMG_BASE + 0x0080)
#define  IMG_BUFF_SIZE                       (_IMG_BASE + 0x0082)
#define  IMG_BUFF_TRIGGER                    (_IMG_BASE + 0x0083)
#define  IMG_BUFF_NUMBUFS                    (_IMG_BASE + 0x00B0)
#define  IMG_BUFF_CHANNEL                    (_IMG_BASE + 0x00Bc)
#define  IMG_BUFF_ACTUALHEIGHT               (_IMG_BASE + 0x0400)
#define  IMG_BUFF_IMAGE                      (_IMG_BASE + 0x0401)


//----------------------------------------------------------------------------
//  Possible Buffer Command Values
//----------------------------------------------------------------------------
#define  IMG_CMD_NEXT                        0x01  // Proceed to next list entry
#define  IMG_CMD_LOOP                        0x02  // Loop back to start of buffer list and continue processing - RING ACQUISITION
#define  IMG_CMD_PASS                        0x04  // Do nothing here
#define  IMG_CMD_STOP                        0x08  // Stop
#define  IMG_CMD_INVALID                     0x10  // Reserved for internal use


//----------------------------------------------------------------------------
//  Possible Triggered Acquisition Actions
//----------------------------------------------------------------------------
#define  IMG_TRIG_ACTION_NONE                0 // no trigger action
#define  IMG_TRIG_ACTION_CAPTURE             1 // one trigger required to start the acquisition once
#define  IMG_TRIG_ACTION_BUFLIST             2 // one trigger required to start the buflist each time
#define  IMG_TRIG_ACTION_BUFFER              3 // one trigger required for each buffer
#define  IMG_TRIG_ACTION_STOP                4 // one trigger is used to stop the acquisition


//----------------------------------------------------------------------------
// Old RTSI mapping constants (imgSessionSetRTSImap)
//----------------------------------------------------------------------------
#define  IMG_TRIG_MAP_RTSI0_DISABLED         0x0000000f
#define  IMG_TRIG_MAP_RTSI0_EXT0             0x00000001
#define  IMG_TRIG_MAP_RTSI0_EXT1             0x00000002
#define  IMG_TRIG_MAP_RTSI0_EXT2             0x00000003
#define  IMG_TRIG_MAP_RTSI0_EXT3             0x00000004
#define  IMG_TRIG_MAP_RTSI0_EXT4             0x00000005
#define  IMG_TRIG_MAP_RTSI0_EXT5             0x00000006
#define  IMG_TRIG_MAP_RTSI0_EXT6             0x00000007

#define  IMG_TRIG_MAP_RTSI1_DISABLED         0x000000f0
#define  IMG_TRIG_MAP_RTSI1_EXT0             0x00000010
#define  IMG_TRIG_MAP_RTSI1_EXT1             0x00000020
#define  IMG_TRIG_MAP_RTSI1_EXT2             0x00000030
#define  IMG_TRIG_MAP_RTSI1_EXT3             0x00000040
#define  IMG_TRIG_MAP_RTSI1_EXT4             0x00000050
#define  IMG_TRIG_MAP_RTSI1_EXT5             0x00000060
#define  IMG_TRIG_MAP_RTSI1_EXT6             0x00000070

#define  IMG_TRIG_MAP_RTSI2_DISABLED         0x00000f00
#define  IMG_TRIG_MAP_RTSI2_EXT0             0x00000100
#define  IMG_TRIG_MAP_RTSI2_EXT1             0x00000200
#define  IMG_TRIG_MAP_RTSI2_EXT2             0x00000300
#define  IMG_TRIG_MAP_RTSI2_EXT3             0x00000400
#define  IMG_TRIG_MAP_RTSI2_EXT4             0x00000500
#define  IMG_TRIG_MAP_RTSI2_EXT5             0x00000600
#define  IMG_TRIG_MAP_RTSI2_EXT6             0x00000700

#define  IMG_TRIG_MAP_RTSI3_DISABLED         0x0000f000
#define  IMG_TRIG_MAP_RTSI3_EXT0             0x00001000
#define  IMG_TRIG_MAP_RTSI3_EXT1             0x00002000
#define  IMG_TRIG_MAP_RTSI3_EXT2             0x00003000
#define  IMG_TRIG_MAP_RTSI3_EXT3             0x00004000
#define  IMG_TRIG_MAP_RTSI3_EXT4             0x00005000
#define  IMG_TRIG_MAP_RTSI3_EXT5             0x00006000
#define  IMG_TRIG_MAP_RTSI3_EXT6             0x00007000


//----------------------------------------------------------------------------
//  Frame timeout values
//----------------------------------------------------------------------------
#define  IMG_FRAMETIME_STANDARD              100      //    100 milliseconds
#define  IMG_FRAMETIME_1SECOND               1000     //   1000 milliseconds -  1 second
#define  IMG_FRAMETIME_2SECONDS              2000     //   2000 milliseconds -  2 seconds
#define  IMG_FRAMETIME_5SECONDS              5000     //   5000 milliseconds -  5 seconds
#define  IMG_FRAMETIME_10SECONDS             10000    //  10000 milliseconds - 10 seconds
#define  IMG_FRAMETIME_1MINUTE               60000    //  60000 milliseconds -  1 minute
#define  IMG_FRAMETIME_2MINUTES              120000   // 120000 milliseconds -  2 minutes
#define  IMG_FRAMETIME_5MINUTES              300000   // 300000 milliseconds -  5 minutes
#define  IMG_FRAMETIME_10MINUTES             600000   // 600000 milliseconds - 10 minutes


//----------------------------------------------------------------------------
//  Gain values
//----------------------------------------------------------------------------
#define  IMG_GAIN_0DB                        0
#define  IMG_GAIN_3DB                        1
#define  IMG_GAIN_6DB                        2


//----------------------------------------------------------------------------
//  Gain values for the 1409
//----------------------------------------------------------------------------
#define  IMG_GAIN_2_00                       0
#define  IMG_GAIN_1_75                       1
#define  IMG_GAIN_1_50                       2
#define  IMG_GAIN_1_00                       3


//----------------------------------------------------------------------------
//  Analog bandwidth
//----------------------------------------------------------------------------
#define  IMG_BANDWIDTH_FULL                  0
#define  IMG_BANDWIDTH_9MHZ                  1


//----------------------------------------------------------------------------
//  White and black reference ranges
//----------------------------------------------------------------------------
#define  IMG_WHITE_REFERENCE_MIN             0
#define  IMG_WHITE_REFERENCE_MAX             63
#define  IMG_BLACK_REFERENCE_MIN             0
#define  IMG_BLACK_REFERENCE_MAX             63


//----------------------------------------------------------------------------
//  Possible Trigger Polarities
//----------------------------------------------------------------------------
#define  IMG_TRIG_POLAR_ACTIVEH              0
#define  IMG_TRIG_POLAR_ACTIVEL              1


//----------------------------------------------------------------------------
//  The Trigger Lines
//  Important!!!  If you change the number of lines or add a different
//  kind of line, be sure to update IsExtTrigLine(), IsRTSILine(), or add
//  a new IsXXXLine() function, as appropriate.
//----------------------------------------------------------------------------
#define  IMG_EXT_TRIG0                       0
#define  IMG_EXT_TRIG1                       1
#define  IMG_EXT_TRIG2                       2
#define  IMG_EXT_TRIG3                       3
#define  IMG_EXT_RTSI0                       4
#define  IMG_EXT_RTSI1                       5
#define  IMG_EXT_RTSI2                       6
#define  IMG_EXT_RTSI3                       7
#define  IMG_EXT_RTSI4                       12
#define  IMG_EXT_RTSI5                       13
#define  IMG_EXT_RTSI6                       14
#define  IMG_TRIG_ROUTE_DISABLED             0xFFFFFFFF


//----------------------------------------------------------------------------
//  Internal Signals
//  These are the signals that you can wait on or use to trigger the start
//  of pulse generation.
//----------------------------------------------------------------------------
#define  IMG_AQ_DONE                         8     // wait for the entire acquisition to complete
#define  IMG_FRAME_START                     9     // wait for the frame to start
#define  IMG_FRAME_DONE                      10    // wait for the frame to complete
#define  IMG_BUF_COMPLETE                    11    // wait for the buffer to complete 
#define  IMG_AQ_IN_PROGRESS                  15
#define  IMG_IMMEDIATE                       16
#define  IMG_FIXED_FREQUENCY                 17    // used in imgSessionLineTrigSrouce (linescan)
#define  IMG_LINE_VALID                      18    // wait for line valid signal (HSYNC)
#define  IMG_FRAME_VALID                     19    // wait for frame valid signal (VSYNC)


//----------------------------------------------------------------------------
//  IMAQ Vision Compatible Image Types.
//----------------------------------------------------------------------------
#define  IMG_IMAGE_U8                        0  // Unsigned 8-bit image
#define  IMG_IMAGE_I16                       1  // Signed 16-bit image
#define  IMG_IMAGE_RGB32                     4  // 32-bit RGB image
#define  IMG_IMAGE_HSL32                     5  // 32-bit HSL image
#define  IMG_IMAGE_RGB64                     6  // 64-bit RGB image


//----------------------------------------------------------------------------
//  Color representations
//----------------------------------------------------------------------------
#define  IMG_COLOR_REP_RGB32                 0  // 32 bits RGB
#define  IMG_COLOR_REP_RED8                  1  // 8 bits Red
#define  IMG_COLOR_REP_GREEN8                2  // 8 bits Green
#define  IMG_COLOR_REP_BLUE8                 3  // 8 bits Blue
#define  IMG_COLOR_REP_LUM8                  4  // 8 bits Light
#define  IMG_COLOR_REP_HUE8                  5  // 8 bits Hue
#define  IMG_COLOR_REP_SAT8                  6  // 8 bits Saturation
#define  IMG_COLOR_REP_INT8                  7  // 8 bits Intensity
#define  IMG_COLOR_REP_LUM16                 8  // 16 bits Light
#define  IMG_COLOR_REP_HUE16                 9  // 16 bits Hue
#define  IMG_COLOR_REP_SAT16                 10 // 16 bits Saturation
#define  IMG_COLOR_REP_INT16                 11 // 16 bits Intensity
#define  IMG_COLOR_REP_RGB48                 12 // 48 bits RGB
#define  IMG_COLOR_REP_RGB24                 13 // 24 bits RGB
#define  IMG_COLOR_REP_RGB16                 14 // 16 bits RGB (x555)
#define  IMG_COLOR_REP_HSL32                 15 // 32 bits HSL
#define  IMG_COLOR_REP_HSI32                 16 // 32 bits HSI
#define  IMG_COLOR_REP_NONE                  17 // No color information. Use bit-depth
#define  IMG_COLOR_REP_MONO10                18 // 10 bit Monochrome


//----------------------------------------------------------------------------
//  Specifies the size of each array element in the interface names array
//----------------------------------------------------------------------------
#define  INTERFACE_NAME_SIZE              256


//----------------------------------------------------------------------------
//  Pulse timebases
//----------------------------------------------------------------------------
#define  PULSE_TIMEBASE_PIXELCLK             0x00000001
#define  PULSE_TIMEBASE_50MHZ                0x00000002
#define  PULSE_TIMEBASE_100KHZ               0x00000003
#define  PULSE_TIMEBASE_SCALED_ENCODER       0x00000004


//----------------------------------------------------------------------------
//  Pulse mode
//----------------------------------------------------------------------------
#define  PULSE_MODE_TRAIN                    0x00000001
#define  PULSE_MODE_SINGLE                   0x00000002
#define  PULSE_MODE_SINGLE_REARM             0x00000003


//----------------------------------------------------------------------------
//  Pulse polarities
//----------------------------------------------------------------------------
#define  IMG_PULSE_POLAR_ACTIVEH             0
#define  IMG_PULSE_POLAR_ACTIVEL             1


//----------------------------------------------------------------------------
//  Trigger drive
//----------------------------------------------------------------------------
#define  IMG_TRIG_DRIVE_DISABLED             0
#define  IMG_TRIG_DRIVE_AQ_IN_PROGRESS       1
#define  IMG_TRIG_DRIVE_AQ_DONE              2
#define  IMG_TRIG_DRIVE_PIXEL_CLK            3
#define  IMG_TRIG_DRIVE_UNASSERTED           4
#define  IMG_TRIG_DRIVE_ASSERTED             5
#define  IMG_TRIG_DRIVE_HSYNC                6
#define  IMG_TRIG_DRIVE_VSYNC                7
#define  IMG_TRIG_DRIVE_FRAME_START          8
#define  IMG_TRIG_DRIVE_FRAME_DONE           9
#define  IMG_TRIG_DRIVE_SCALED_ENCODER       10


//----------------------------------------------------------------------------
//  imgPlot Flags
//----------------------------------------------------------------------------
#define  IMGPLOT_MONO_8                      0x00000000
#define  IMGPLOT_INVERT                      0x00000001
#define  IMGPLOT_COLOR_RGB24                 0x00000002
#define  IMGPLOT_COLOR_RGB32                 0x00000004
#define  IMGPLOT_MONO_10                     0x00000008
#define  IMGPLOT_MONO_12                     0x00000010
#define  IMGPLOT_MONO_14                     0x00000020
#define  IMGPLOT_MONO_16                     0x00000040
#define  IMGPLOT_MONO_32                     0x00000080
#define  IMGPLOT_AUTO                        0x00000100


//----------------------------------------------------------------------------
//  Stillcolor modes.  OBSOLETE.
//----------------------------------------------------------------------------
#define  IMG_COLOR_MODE_DISABLED             0        // Color mode disabled
#define  IMG_COLOR_MODE_RGB                  1        // Color mode RGB StillColor
#define  IMG_COLOR_MODE_COMPOSITE_STLC       2        // Color mode Composite StillColor


//----------------------------------------------------------------------------
//  Signal states
//----------------------------------------------------------------------------
typedef enum {
   IMG_SIGNAL_STATE_RISING  = 0,
   IMG_SIGNAL_STATE_FALLING = 1,
   IMG_SIGNAL_STATE_HIGH    = 2,
   IMG_SIGNAL_STATE_LOW     = 3,
   IMG_SIGNAL_STATE_HI_Z    = 4
} IMG_SIGNAL_STATE;


//----------------------------------------------------------------------------
//  ROI Fit Modes
//----------------------------------------------------------------------------
typedef enum {
    IMG_ROI_FIT_LARGER,
    IMG_ROI_FIT_SMALLER
} IMG_ROI_FIT_MODE;


//----------------------------------------------------------------------------
//  Signal Types
//----------------------------------------------------------------------------
typedef enum {
    IMG_SIGNAL_NONE                 = 0xFFFFFFFF,
    IMG_SIGNAL_EXTERNAL             = 0,
    IMG_SIGNAL_RTSI                 = 1,
    IMG_SIGNAL_ISO_IN               = 2,
    IMG_SIGNAL_ISO_OUT              = 3,
    IMG_SIGNAL_STATUS               = 4,
    IMG_SIGNAL_SCALED_ENCODER       = 5,
    IMG_SIGNAL_SOFTWARE_TRIGGER     = 6
} IMG_SIGNAL_TYPE;
   

//----------------------------------------------------------------------------
//  Overwrite Modes
//----------------------------------------------------------------------------
typedef enum {
    IMG_OVERWRITE_GET_OLDEST         = 0,
    IMG_OVERWRITE_GET_NEXT_ITERATION = 1,
    IMG_OVERWRITE_FAIL               = 2,
    IMG_OVERWRITE_GET_NEWEST         = 3
} IMG_OVERWRITE_MODE;


//----------------------------------------------------------------------------
//  Sensor Scan Modes
//----------------------------------------------------------------------------
typedef enum {
    IMG_SENSOR_PARTIAL_SCAN_OFF     = 0,
    IMG_SENSOR_PARTIAL_SCAN_HALF    = 1,
    IMG_SENSOR_PARTIAL_SCAN_QUARTER = 2
} IMG_SENSOR_PARTIAL_SCAN;


//----------------------------------------------------------------------------
//  Sensor Binning Modes
//----------------------------------------------------------------------------
typedef enum {
    IMG_SENSOR_BINNING_OFF = 0,
    IMG_SENSOR_BINNING_1x2 = 1,
} IMG_SENSOR_BINNING;


//----------------------------------------------------------------------------
//  LED States
//----------------------------------------------------------------------------
typedef enum {
    IMG_LED_OFF = 0,
    IMG_LED_ON  = 1
} IMG_LED_STATE;


//----------------------------------------------------------------------------
//  Timebases
//----------------------------------------------------------------------------
typedef enum {
    IMG_TIMEBASE_PIXELCLK       = 1,
    IMG_TIMEBASE_50MHZ          = 2,
    IMG_TIMEBASE_100KHZ         = 3,
    IMG_TIMEBASE_SCALED_ENCODER = 4,
    IMG_TIMEBASE_MILLISECONDS   = 5
} IMG_TIMEBASE;


//----------------------------------------------------------------------------
//  Buffer location specifier.
//----------------------------------------------------------------------------
#define IMG_HOST_FRAME                    0
#define IMG_DEVICE_FRAME                  1


//----------------------------------------------------------------------------
//  Bayer decoding pattern.
//----------------------------------------------------------------------------
#define  IMG_BAYER_PATTERN_GBGB_RGRG      0
#define  IMG_BAYER_PATTERN_GRGR_BGBG      1
#define  IMG_BAYER_PATTERN_BGBG_GRGR      2
#define  IMG_BAYER_PATTERN_RGRG_GBGB      3


//----------------------------------------------------------------------------
//  Internal Lighting Modes
//----------------------------------------------------------------------------
typedef enum {
    IMG_LIGHTING_OFF = 0,
    IMG_LIGHTING_CONTINUOUS = 1,
    IMG_LIGHTING_STROBED = 2
} IMG_LIGHTING_MODE;


//----------------------------------------------------------------------------
//  External Lighting Modes
//----------------------------------------------------------------------------
typedef enum {
    IMG_LIGHTING_EXTERNAL_STROBE_OFF = 0,
    IMG_LIGHTING_EXTERNAL_STROBE_RISING = 1,
    IMG_LIGHTING_EXTERNAL_STROBE_FALLING = 2
} IMG_LIGHTING_EXTERNAL_STROBE_MODE;


//----------------------------------------------------------------------------
//  Callback pointer definition 
//----------------------------------------------------------------------------
typedef  uInt32 (NI_CDECL * CALL_BACK_PTR)(SESSION_ID boardid, IMG_ERR err, uInt32 signal, void* data);
typedef  uInt32 (NI_CDECL * CALL_BACK_PTR2)(SESSION_ID boardid, IMG_ERR err, IMG_SIGNAL_TYPE signalType, uInt32 signalIdentifier, void* data);


//============================================================================
//  Error Codes
//============================================================================
#define _IMG_ERR                                0xBFF60000
#define IMG_ERR_GOOD                            0                    // no error

//----------------------------------------------------------------------------
//  Warnings
//----------------------------------------------------------------------------
#define  IMG_WRN_BCAM                           (_IMG_BASE + 0x0001)  // corrupt camera file detected
#define  IMG_WRN_CONF                           (_IMG_BASE + 0x0002)  // change requires reconfigure to take effect
#define  IMG_WRN_ILCK                           (_IMG_BASE + 0x0003)  // interface still locked
#define  IMG_WRN_BLKG                           (_IMG_BASE + 0x0004)  // STC: unstable blanking reference
#define  IMG_WRN_BRST                           (_IMG_BASE + 0x0005)  // STC: bad quality colorburst
#define  IMG_WRN_OATTR                          (_IMG_BASE + 0x0006)  // old attribute used
#define  IMG_WRN_WLOR                           (_IMG_BASE + 0x0007)  // white level out of range
#define  IMG_WRN_IATTR                          (_IMG_BASE + 0x0008)  // invalid attribute in current state
#define  IMG_WRN_LATEST                         (_IMG_BASE + 0x000A)

//----------------------------------------------------------------------------
//  Old errors (from 2.X)
//----------------------------------------------------------------------------
#define  IMG_ERR_NCAP                           (_IMG_ERR + 0x0001)  // function not implemented
#define  IMG_ERR_OVRN                           (_IMG_ERR + 0x0002)  // too many interfaces open
#define  IMG_ERR_EMEM                           (_IMG_ERR + 0x0003)  // could not allocate memory in user mode (calloc failed)
#define  IMG_ERR_OSER                           (_IMG_ERR + 0x0004)  // operating system error occurred
#define  IMG_ERR_PAR1                           (_IMG_ERR + 0x0005)  // Error with parameter 1
#define  IMG_ERR_PAR2                           (_IMG_ERR + 0x0006)  // Error with parameter 2
#define  IMG_ERR_PAR3                           (_IMG_ERR + 0x0007)  // Error with parameter 3
#define  IMG_ERR_PAR4                           (_IMG_ERR + 0x0008)  // Error with parameter 4
#define  IMG_ERR_PAR5                           (_IMG_ERR + 0x0009)  // Error with parameter 5
#define  IMG_ERR_PAR6                           (_IMG_ERR + 0x000A)  // Error with parameter 6
#define  IMG_ERR_PAR7                           (_IMG_ERR + 0x000B)  // Error with parameter 7
#define  IMG_ERR_MXBF                           (_IMG_ERR + 0x000C)  // too many buffers already allocated
#define  IMG_ERR_DLLE                           (_IMG_ERR + 0x000D)  // DLL internal error - bad logic state
#define  IMG_ERR_BSIZ                           (_IMG_ERR + 0x000E)  // buffer size used is too small for minimum acquisition frame
#define  IMG_ERR_MXBI                           (_IMG_ERR + 0x000F)  // exhausted buffer id's
#define  IMG_ERR_ELCK                           (_IMG_ERR + 0x0010)  // not enough physical memory - the system could not allocate page locked memory
#define  IMG_ERR_DISE                           (_IMG_ERR + 0x0011)  // error releasing the image buffer
#define  IMG_ERR_BBUF                           (_IMG_ERR + 0x0012)  // bad buffer pointer in list
#define  IMG_ERR_NLCK                           (_IMG_ERR + 0x0013)  // buffer list is not locked
#define  IMG_ERR_NCAM                           (_IMG_ERR + 0x0014)  // no camera defined for this channel
#define  IMG_ERR_BINT                           (_IMG_ERR + 0x0015)  // bad interface
#define  IMG_ERR_BROW                           (_IMG_ERR + 0x0016)  // rowbytes is less than region of interest
#define  IMG_ERR_BROI                           (_IMG_ERR + 0x0017)  // bad region of interest; check width, heigh, rowpixels, and scaling
#define  IMG_ERR_BCMF                           (_IMG_ERR + 0x0018)  // bad camera file (check syntax)
#define  IMG_ERR_NVBL                           (_IMG_ERR + 0x0019)  // not successful because of hardware limitations
#define  IMG_ERR_NCFG                           (_IMG_ERR + 0x001A)  // invalid action - no buffers configured for session
#define  IMG_ERR_BBLF                           (_IMG_ERR + 0x001B)  // buffer list does not contain a valid final command
#define  IMG_ERR_BBLE                           (_IMG_ERR + 0x001C)  // buffer list does contains an invalid command
#define  IMG_ERR_BBLB                           (_IMG_ERR + 0x001D)  // a buffer list buffer is null
#define  IMG_ERR_NAIP                           (_IMG_ERR + 0x001E)  // no acquisition in progress
#define  IMG_ERR_VLCK                           (_IMG_ERR + 0x001F)  // can't get video lock
#define  IMG_ERR_BDMA                           (_IMG_ERR + 0x0020)  // bad DMA transfer
#define  IMG_ERR_AIOP                           (_IMG_ERR + 0x0021)  // can't perform request - acquisition in progress
#define  IMG_ERR_TIMO                           (_IMG_ERR + 0x0022)  // wait timed out - acquisition not complete
#define  IMG_ERR_NBUF                           (_IMG_ERR + 0x0023)  // no buffers available - too early in acquisition
#define  IMG_ERR_ZBUF                           (_IMG_ERR + 0x0024)  // zero buffer size - no bytes filled
#define  IMG_ERR_HLPR                           (_IMG_ERR + 0x0025)  // bad parameter to low level - check attributes and high level arguments
#define  IMG_ERR_BTRG                           (_IMG_ERR + 0x0026)  // trigger loopback problem - can't drive trigger with action enabled
#define  IMG_ERR_NINF                           (_IMG_ERR + 0x0027)  // no interface found
#define  IMG_ERR_NDLL                           (_IMG_ERR + 0x0028)  // unable to load DLL
#define  IMG_ERR_NFNC                           (_IMG_ERR + 0x0029)  // unable to find API function in DLL
#define  IMG_ERR_NOSR                           (_IMG_ERR + 0x002A)  // unable to allocate system resources (CVI only)
#define  IMG_ERR_BTAC                           (_IMG_ERR + 0x002B)  // no trigger action - acquisition will time out
#define  IMG_ERR_FIFO                           (_IMG_ERR + 0x002C)  // fifo overflow caused acquisition to halt
#define  IMG_ERR_MLCK                           (_IMG_ERR + 0x002D)  // memory lock error - the system could not page lock the buffer(s)
#define  IMG_ERR_ILCK                           (_IMG_ERR + 0x002E)  // interface locked
#define  IMG_ERR_NEPK                           (_IMG_ERR + 0x002F)  // no external pixel clock
#define  IMG_ERR_SCLM                           (_IMG_ERR + 0x0030)  // field scaling mode not supported
#define  IMG_ERR_SCC1                           (_IMG_ERR + 0x0031)  // still color rgb, channel not set to 1
#define  IMG_ERR_SMALLALLOC                     (_IMG_ERR + 0x0032)  // Error during small buffer allocation
#define  IMG_ERR_ALLOC                          (_IMG_ERR + 0x0033)  // Error during large buffer allocation
#define  IMG_ERR_BADCAMTYPE                     (_IMG_ERR + 0x0034)  // Bad camera type - (Not a NTSC or PAL)
#define  IMG_ERR_BADPIXTYPE                     (_IMG_ERR + 0x0035)  // Camera not supported (not 8 bits)
#define  IMG_ERR_BADCAMPARAM                    (_IMG_ERR + 0x0036)  // Bad camera parameter from the configuration file
#define  IMG_ERR_PALKEYDTCT                     (_IMG_ERR + 0x0037)  // PAL key detection error
#define  IMG_ERR_BFRQ                           (_IMG_ERR + 0x0038)  // Bad frequency values
#define  IMG_ERR_BITP                           (_IMG_ERR + 0x0039)  // Bad interface type
#define  IMG_ERR_HWNC                           (_IMG_ERR + 0x003A)  // Hardware not capable of supporting this
#define  IMG_ERR_SERIAL                         (_IMG_ERR + 0x003B)  // serial port error
#define  IMG_ERR_MXPI                           (_IMG_ERR + 0x003C)  // exhausted pulse id's
#define  IMG_ERR_BPID                           (_IMG_ERR + 0x003D)  // bad pulse id
#define  IMG_ERR_NEVR                           (_IMG_ERR + 0x003E)  // should never get this error - bad code!
#define  IMG_ERR_SERIAL_TIMO                    (_IMG_ERR + 0x003F)  // serial transmit/receive timeout
#define  IMG_ERR_PG_TOO_MANY                    (_IMG_ERR + 0x0040)  // too many PG transitions defined
#define  IMG_ERR_PG_BAD_TRANS                   (_IMG_ERR + 0x0041)  // bad PG transition time
#define  IMG_ERR_PLNS                           (_IMG_ERR + 0x0042)  // pulse not started error
#define  IMG_ERR_BPMD                           (_IMG_ERR + 0x0043)  // bad pulse mode
#define  IMG_ERR_NSAT                           (_IMG_ERR + 0x0044)  // non settable attribute
#define  IMG_ERR_HYBRID                         (_IMG_ERR + 0x0045)  // can't mix onboard and system memory buffers
#define  IMG_ERR_BADFILFMT                      (_IMG_ERR + 0x0046)  // the pixel depth is not supported by this file format
#define  IMG_ERR_BADFILEXT                      (_IMG_ERR + 0x0047)  // This file extension is not supported
#define  IMG_ERR_NRTSI                          (_IMG_ERR + 0x0048)  // exhausted RTSI map registers
#define  IMG_ERR_MXTRG                          (_IMG_ERR + 0x0049)  // exhausted trigger resources
#define  IMG_ERR_MXRC                           (_IMG_ERR + 0x004A)  // exhausted resources (general)
#define  IMG_ERR_OOR                            (_IMG_ERR + 0x004B)  // parameter out of range
#define  IMG_ERR_NPROG                          (_IMG_ERR + 0x004C)  // FPGA not programmed
#define  IMG_ERR_NEOM                           (_IMG_ERR + 0x004D)  // not enough onboard memory to perform operation
#define  IMG_ERR_BDTYPE                         (_IMG_ERR + 0x004E)  // bad display type -- buffer cannot be displayed with imgPlot
#define  IMG_ERR_THRDACCDEN                     (_IMG_ERR + 0x004F)  // thread denied access to function
#define  IMG_ERR_BADFILWRT                      (_IMG_ERR + 0x0050)  // Could not write the file
#define  IMG_ERR_AEXM                           (_IMG_ERR + 0x0051)  // Already called ExamineBuffer once.  Call ReleaseBuffer.

//----------------------------------------------------------------------------
//  New Error codes (3.0)
//----------------------------------------------------------------------------
#define IMG_ERR_FIRST_ERROR IMG_ERR_NCAP
#define  IMG_ERR_NOT_SUPPORTED                      (_IMG_ERR + 0x0001)  // function not implemented
#define  IMG_ERR_SYSTEM_MEMORY_FULL                 (_IMG_ERR + 0x0003)  // could not allocate memory in user mode (calloc failed)
#define  IMG_ERR_BUFFER_SIZE_TOO_SMALL              (_IMG_ERR + 0x000E)  // buffer size used is too small for minimum acquisition frame
#define  IMG_ERR_BUFFER_LIST_NOT_LOCKED             (_IMG_ERR + 0x0013)  // buffer list is not locked
#define  IMG_ERR_BAD_INTERFACE_FILE                 (_IMG_ERR + 0x0015)  // bad interface
#define  IMG_ERR_BAD_USER_RECT                      (_IMG_ERR + 0x0017)  // bad region of interest; check width, heigh, rowpixels, and scaling
#define  IMG_ERR_BAD_CAMERA_FILE                    (_IMG_ERR + 0x0018)  // bad camera file (check syntax)
#define  IMG_ERR_NO_BUFFERS_CONFIGURED              (_IMG_ERR + 0x001A)  // invalid action - no buffers configured for session
#define  IMG_ERR_BAD_BUFFER_LIST_FINAL_COMMAND      (_IMG_ERR + 0x001B)  // buffer list does not contain a valid final command
#define  IMG_ERR_BAD_BUFFER_LIST_COMMAND            (_IMG_ERR + 0x001C)  // buffer list does contains an invalid command
#define  IMG_ERR_BAD_BUFFER_POINTER                 (_IMG_ERR + 0x001D)  // a buffer list buffer is null
#define  IMG_ERR_BOARD_NOT_RUNNING                  (_IMG_ERR + 0x001E)  // no acquisition in progress
#define  IMG_ERR_VIDEO_LOCK                         (_IMG_ERR + 0x001F)  // can't get video lock
#define  IMG_ERR_BOARD_RUNNING                      (_IMG_ERR + 0x0021)  // can't perform request - acquisition in progress
#define  IMG_ERR_TIMEOUT                            (_IMG_ERR + 0x0022)  // wait timed out - acquisition not complete
#define  IMG_ERR_ZERO_BUFFER_SIZE                   (_IMG_ERR + 0x0024)  // zero buffer size - no bytes filled
#define  IMG_ERR_NO_INTERFACE_FOUND                 (_IMG_ERR + 0x0027)  // no interface found
#define  IMG_ERR_FIFO_OVERFLOW                      (_IMG_ERR + 0x002C)  // fifo overflow caused acquisition to halt
#define  IMG_ERR_MEMORY_PAGE_LOCK_FAULT             (_IMG_ERR + 0x002D)  // memory lock error - the system could not page lock the buffer(s)
#define  IMG_ERR_BAD_CLOCK_FREQUENCY                (_IMG_ERR + 0x0038)  // Bad frequency values
#define  IMG_ERR_BAD_CAMERA_TYPE                    (_IMG_ERR + 0x0034)  // Bad camera type - (Not a NTSC or PAL)
#define  IMG_ERR_HARDWARE_NOT_CAPABLE               (_IMG_ERR + 0x003A)  // Hardware not capable of supporting this
#define  IMG_ERR_ATTRIBUTE_NOT_SETTABLE             (_IMG_ERR + 0x0044)  // non settable attribute
#define  IMG_ERR_ONBOARD_MEMORY_FULL                (_IMG_ERR + 0x004D)  // not enough onboard memory to perform operation
#define  IMG_ERR_BUFFER_NOT_RELEASED                (_IMG_ERR + 0x0051)  // Already called ExamineBuffer once.  Call ReleaseBuffer.
#define  IMG_ERR_BAD_LUT_TYPE                       (_IMG_ERR + 0x0052)  // Invalid LUT type
#define  IMG_ERR_ATTRIBUTE_NOT_READABLE             (_IMG_ERR + 0x0053)  // non readable attribute
#define  IMG_ERR_BOARD_NOT_SUPPORTED                (_IMG_ERR + 0x0054)  // This version of the driver doesn't support the board.
#define  IMG_ERR_BAD_FRAME_FIELD                    (_IMG_ERR + 0x0055)  // The value for frame/field was invalid.
#define  IMG_ERR_INVALID_ATTRIBUTE                  (_IMG_ERR + 0x0056)  // The requested attribute is invalid.
#define  IMG_ERR_BAD_LINE_MAP                       (_IMG_ERR + 0x0057)  // The line map is invalid
#define  IMG_ERR_BAD_CHANNEL                        (_IMG_ERR + 0x0059)  // The requested channel is invalid.
#define  IMG_ERR_BAD_CHROMA_FILTER                  (_IMG_ERR + 0x005A)  // The value for the anti-chrominance filter is invalid.
#define  IMG_ERR_BAD_SCALE                          (_IMG_ERR + 0x005B)  // The value for scaling is invalid.
#define  IMG_ERR_BAD_TRIGGER_MODE                   (_IMG_ERR + 0x005D)  // The value for trigger mode is invalid.
#define  IMG_ERR_BAD_CLAMP_START                    (_IMG_ERR + 0x005E)  // The value for clamp start is invalid.
#define  IMG_ERR_BAD_CLAMP_STOP                     (_IMG_ERR + 0x005F)  // The value for clamp stop is invalid.
#define  IMG_ERR_BAD_BRIGHTNESS                     (_IMG_ERR + 0x0060)  // The brightness level is out of range
#define  IMG_ERR_BAD_CONTRAST                       (_IMG_ERR + 0x0061)  // The constrast  level is out of range
#define  IMG_ERR_BAD_SATURATION                     (_IMG_ERR + 0x0062)  // The saturation level is out of range
#define  IMG_ERR_BAD_TINT                           (_IMG_ERR + 0x0063)  // The tint level is out of range
#define  IMG_ERR_BAD_HUE_OFF_ANGLE                  (_IMG_ERR + 0x0064)  // The hue offset angle is out of range.
#define  IMG_ERR_BAD_ACQUIRE_FIELD                  (_IMG_ERR + 0x0065)  // The value for acquire field is invalid.
#define  IMG_ERR_BAD_LUMA_BANDWIDTH                 (_IMG_ERR + 0x0066)  // The value for luma bandwidth is invalid.
#define  IMG_ERR_BAD_LUMA_COMB                      (_IMG_ERR + 0x0067)  // The value for luma comb is invalid.
#define  IMG_ERR_BAD_CHROMA_PROCESS                 (_IMG_ERR + 0x0068)  // The value for chroma processing is invalid.
#define  IMG_ERR_BAD_CHROMA_BANDWIDTH               (_IMG_ERR + 0x0069)  // The value for chroma bandwidth is invalid.
#define  IMG_ERR_BAD_CHROMA_COMB                    (_IMG_ERR + 0x006A)  // The value for chroma comb is invalid.
#define  IMG_ERR_BAD_RGB_CORING                     (_IMG_ERR + 0x006B)  // The value for RGB coring is invalid.
#define  IMG_ERR_BAD_HUE_REPLACE_VALUE              (_IMG_ERR + 0x006C)  // The value for HSL hue replacement is out of range.
#define  IMG_ERR_BAD_RED_GAIN                       (_IMG_ERR + 0x006D)  // The value for red gain is out of range.
#define  IMG_ERR_BAD_GREEN_GAIN                     (_IMG_ERR + 0x006E)  // The value for green gain is out of range.
#define  IMG_ERR_BAD_BLUE_GAIN                      (_IMG_ERR + 0x006F)  // The value for blue gain is out of range.
#define  IMG_ERR_BAD_START_FIELD                    (_IMG_ERR + 0x0070)  // Invalid start field
#define  IMG_ERR_BAD_TAP_DIRECTION                  (_IMG_ERR + 0x0071)  // Invalid tap scan direction
#define  IMG_ERR_BAD_MAX_IMAGE_RECT                 (_IMG_ERR + 0x0072)  // Invalid maximum image rect
#define  IMG_ERR_BAD_TAP_TYPE                       (_IMG_ERR + 0x0073)  // Invalid tap configuration type
#define  IMG_ERR_BAD_SYNC_RECT                      (_IMG_ERR + 0x0074)  // Invalid sync rect
#define  IMG_ERR_BAD_ACQWINDOW_RECT                 (_IMG_ERR + 0x0075)  // Invalid acquisition window
#define  IMG_ERR_BAD_HSL_CORING                     (_IMG_ERR + 0x0076)  // The value for HSL coring is out of range.
#define  IMG_ERR_BAD_TAP_0_VALID_RECT               (_IMG_ERR + 0x0077)  // Invalid tap 0 valid rect
#define  IMG_ERR_BAD_TAP_1_VALID_RECT               (_IMG_ERR + 0x0078)  // Invalid tap 1 valid rect
#define  IMG_ERR_BAD_TAP_2_VALID_RECT               (_IMG_ERR + 0x0079)  // Invalid tap 2 valid rect
#define  IMG_ERR_BAD_TAP_3_VALID_RECT               (_IMG_ERR + 0x007A)  // Invalid tap 3 valid rect
#define  IMG_ERR_BAD_TAP_RECT                       (_IMG_ERR + 0x007B)  // Invalid tap rect
#define  IMG_ERR_BAD_NUM_TAPS                       (_IMG_ERR + 0x007C)  // Invalid number of taps
#define  IMG_ERR_BAD_TAP_NUM                        (_IMG_ERR + 0x007D)  // Invalid tap number
#define  IMG_ERR_BAD_QUAD_NUM                       (_IMG_ERR + 0x007E)  // Invalid Scarab quadrant number
#define  IMG_ERR_BAD_NUM_DATA_LINES                 (_IMG_ERR + 0x007F)  // Invalid number of requested data lines
#define  IMG_ERR_BAD_BITS_PER_COMPONENT             (_IMG_ERR + 0x0080)  // The value for bits per component is invalid.
#define  IMG_ERR_BAD_NUM_COMPONENTS                 (_IMG_ERR + 0x0081)  // The value for number of components is invalid.
#define  IMG_ERR_BAD_BIN_THRESHOLD_LOW              (_IMG_ERR + 0x0082)  // The value for the lower binary threshold is out of range.
#define  IMG_ERR_BAD_BIN_THRESHOLD_HIGH             (_IMG_ERR + 0x0083)  // The value for the upper binary threshold is out of range.
#define  IMG_ERR_BAD_BLACK_REF_VOLT                 (_IMG_ERR + 0x0084)  // The value for the black reference voltage is out of range.
#define  IMG_ERR_BAD_WHITE_REF_VOLT                 (_IMG_ERR + 0x0085)  // The value for the white reference voltage is out of range.
#define  IMG_ERR_BAD_FREQ_STD                       (_IMG_ERR + 0x0086)  // The value for the 6431 frequency standard is out of range.
#define  IMG_ERR_BAD_HDELAY                         (_IMG_ERR + 0x0087)  // The value for HDELAY is out of range.
#define  IMG_ERR_BAD_LOCK_SPEED                     (_IMG_ERR + 0x0088)  // Invalid lock speed.
#define  IMG_ERR_BAD_BUFFER_LIST                    (_IMG_ERR + 0x0089)  // Invalid buffer list
#define  IMG_ERR_BOARD_NOT_INITIALIZED              (_IMG_ERR + 0x008A)  // An attempt was made to access the board before it was initialized.
#define  IMG_ERR_BAD_PCLK_SOURCE                    (_IMG_ERR + 0x008B)  // Invalid pixel clock source
#define  IMG_ERR_BAD_VIDEO_LOCK_CHANNEL             (_IMG_ERR + 0x008C)  // Invalid video lock source
#define  IMG_ERR_BAD_LOCK_SEL                       (_IMG_ERR + 0x008D)  // Invalid locking mode
#define  IMG_ERR_BAD_BAUD_RATE                      (_IMG_ERR + 0x008E)  // Invalid baud rate for the UART
#define  IMG_ERR_BAD_STOP_BITS                      (_IMG_ERR + 0x008F)  // The number of stop bits for the UART is out of range.
#define  IMG_ERR_BAD_DATA_BITS                      (_IMG_ERR + 0x0090)  // The number of data bits for the UART is out of range.
#define  IMG_ERR_BAD_PARITY                         (_IMG_ERR + 0x0091)  // Invalid parity setting for the UART
#define  IMG_ERR_TERM_STRING_NOT_FOUND              (_IMG_ERR + 0x0092)  // Couldn't find the termination string in a serial read
#define  IMG_ERR_SERIAL_READ_TIMEOUT                (_IMG_ERR + 0x0093)  // Exceeded the user specified timeout for a serial read
#define  IMG_ERR_SERIAL_WRITE_TIMEOUT               (_IMG_ERR + 0x0094)  // Exceeded the user specified timeout for a serial write
#define  IMG_ERR_BAD_SYNCHRONICITY                  (_IMG_ERR + 0x0095)  // Invalid setting for whether the acquisition is synchronous.
#define  IMG_ERR_BAD_INTERLACING_CONFIG             (_IMG_ERR + 0x0096)  // Bad interlacing configuration
#define  IMG_ERR_BAD_CHIP_CODE                      (_IMG_ERR + 0x0098)  // Bad chip code.  Couldn't find a matching chip.
#define  IMG_ERR_LUT_NOT_PRESENT                    (_IMG_ERR + 0x0099)  // The LUT chip doesn't exist
#define  IMG_ERR_DSPFILTER_NOT_PRESENT              (_IMG_ERR + 0x009A)  // The DSP filter doesn't exist
#define  IMG_ERR_DEVICE_NOT_FOUND                   (_IMG_ERR + 0x009B)  // The IMAQ device was not found
#define  IMG_ERR_ONBOARD_MEM_CONFIG                 (_IMG_ERR + 0x009C)  // There was a problem while configuring onboard memory
#define  IMG_ERR_BAD_POINTER                        (_IMG_ERR + 0x009D)  // The pointer is bad.  It might be NULL when it shouldn't be NULL or non-NULL when it should be NULL.
#define  IMG_ERR_BAD_BUFFER_LIST_INDEX              (_IMG_ERR + 0x009E)  // The given buffer list index is invalid
#define  IMG_ERR_INVALID_BUFFER_ATTRIBUTE           (_IMG_ERR + 0x009F)  // The given buffer attribute is invalid
#define  IMG_ERR_INVALID_BUFFER_PTR                 (_IMG_ERR + 0x00A0)  // The given buffer wan't created by the NI-IMAQ driver
#define  IMG_ERR_BUFFER_LIST_ALREADY_LOCKED         (_IMG_ERR + 0x00A1)  // A buffer list is already locked down in memory for this device
#define  IMG_ERR_BAD_DEVICE_TYPE                    (_IMG_ERR + 0x00A2)  // The type of IMAQ device is invalid
#define  IMG_ERR_BAD_BAR_SIZE                       (_IMG_ERR + 0x00A3)  // The size of one or more BAR windows is incorrect
#define  IMG_ERR_NO_VALID_COUNTER_RECT              (_IMG_ERR + 0x00A5)  // Couldn't settle on a valid counter rect
#define  IMG_ERR_ACQ_STOPPED                        (_IMG_ERR + 0x00A6)  // The wait terminated because the acquisition stopped.
#define  IMG_ERR_BAD_TRIGGER_ACTION                 (_IMG_ERR + 0x00A7)  // The trigger action is invalid.
#define  IMG_ERR_BAD_TRIGGER_POLARITY               (_IMG_ERR + 0x00A8)  // The trigger polarity is invalid.
#define  IMG_ERR_BAD_TRIGGER_NUMBER                 (_IMG_ERR + 0x00A9)  // The requested trigger line is invalid.
#define  IMG_ERR_BUFFER_NOT_AVAILABLE               (_IMG_ERR + 0x00AA)  // The requested buffer has been overwritten and is no longer available.
#define  IMG_ERR_BAD_PULSE_ID                       (_IMG_ERR + 0x00AC)  // The given pulse id is invalid
#define  IMG_ERR_BAD_PULSE_TIMEBASE                 (_IMG_ERR + 0x00AD)  // The given timebase is invalid.
#define  IMG_ERR_BAD_PULSE_GATE                     (_IMG_ERR + 0x00AE)  // The given gate signal for the pulse is invalid.
#define  IMG_ERR_BAD_PULSE_GATE_POLARITY            (_IMG_ERR + 0x00AF)  // The polarity of the gate signal is invalid.
#define  IMG_ERR_BAD_PULSE_OUTPUT                   (_IMG_ERR + 0x00B0)  // The given output signal for the pulse is invalid.
#define  IMG_ERR_BAD_PULSE_OUTPUT_POLARITY          (_IMG_ERR + 0x00B1)  // The polarity of the output signal is invalid.
#define  IMG_ERR_BAD_PULSE_MODE                     (_IMG_ERR + 0x00B2)  // The given pulse mode is invalid.
#define  IMG_ERR_NOT_ENOUGH_RESOURCES               (_IMG_ERR + 0x00B3)  // There are not enough resources to complete the requested operation.
#define  IMG_ERR_INVALID_RESOURCE                   (_IMG_ERR + 0x00B4)  // The requested resource is invalid
#define  IMG_ERR_BAD_FVAL_ENABLE                    (_IMG_ERR + 0x00B5)  // Invalid enable mode for FVAL
#define  IMG_ERR_BAD_WRITE_ENABLE_MODE              (_IMG_ERR + 0x00B6)  // Invalid combination of enables to write to DRAM
#define  IMG_ERR_COMPONENT_MISMATCH                 (_IMG_ERR + 0x00B7)  // Internal Error: The installed components of the driver are incompatible.  Reinstall the driver.
#define  IMG_ERR_FPGA_PROGRAMMING_FAILED            (_IMG_ERR + 0x00B8)  // Internal Error: Downloading the program to an FPGA didn't work.
#define  IMG_ERR_CONTROL_FPGA_FAILED                (_IMG_ERR + 0x00B9)  // Internal Error: The Control FPGA didn't initialize properly
#define  IMG_ERR_CHIP_NOT_READABLE                  (_IMG_ERR + 0x00BA)  // Internal Error: Attempt to read a write-only chip.
#define  IMG_ERR_CHIP_NOT_WRITABLE                  (_IMG_ERR + 0x00BB)  // Internal Error: Attempt to write a read-only chip.
#define  IMG_ERR_I2C_BUS_FAILED                     (_IMG_ERR + 0x00BC)  // Internal Error: The I2C bus didn't respond correctly.
#define  IMG_ERR_DEVICE_IN_USE                      (_IMG_ERR + 0x00BD)  // The requested IMAQ device is already open
#define  IMG_ERR_BAD_TAP_DATALANES                  (_IMG_ERR + 0x00BE)  // The requested data lanes on a particular tap are invalid
#define  IMG_ERR_BAD_VIDEO_GAIN                     (_IMG_ERR + 0x00BF)  // Bad video gain value
#define  IMG_ERR_VHA_MODE_NOT_ALLOWED               (_IMG_ERR + 0x00C0)  // VHA mode not allowed, based upon the current configuration
#define  IMG_ERR_BAD_TRACKING_SPEED                 (_IMG_ERR + 0x00C1)  // Bad color video tracking speed
#define  IMG_ERR_BAD_COLOR_INPUT_SELECT             (_IMG_ERR + 0x00C2)  // Invalid input select for the 1411
#define  IMG_ERR_BAD_HAV_OFFSET                     (_IMG_ERR + 0x00C3)  // Invalid HAV offset
#define  IMG_ERR_BAD_HS1_OFFSET                     (_IMG_ERR + 0x00C4)  // Invalid HS1 offset
#define  IMG_ERR_BAD_HS2_OFFSET                     (_IMG_ERR + 0x00C5)  // Invalid HS2 offset
#define  IMG_ERR_BAD_IF_CHROMA                      (_IMG_ERR + 0x00C6)  // Invalid chroma IF compensation
#define  IMG_ERR_BAD_COLOR_OUTPUT_FORMAT            (_IMG_ERR + 0x00C7)  // Invalid format for color output
#define  IMG_ERR_BAD_SAMSUNG_SCHCMP                 (_IMG_ERR + 0x00C8)  // Invalid phase constant
#define  IMG_ERR_BAD_SAMSUNG_CDLY                   (_IMG_ERR + 0x00C9)  // Invalid chroma path group delay
#define  IMG_ERR_BAD_SECAM_DETECT                   (_IMG_ERR + 0x00CA)  // Invalid method for secam detection
#define  IMG_ERR_BAD_FSC_DETECT                     (_IMG_ERR + 0x00CB)  // Invalid method for fsc detection
#define  IMG_ERR_BAD_SAMSUNG_CFTC                   (_IMG_ERR + 0x00CC)  // Invalid chroma frequency tracking time constant
#define  IMG_ERR_BAD_SAMSUNG_CGTC                   (_IMG_ERR + 0x00CD)  // Invalid chroma gain tracking time constant
#define  IMG_ERR_BAD_SAMSUNG_SAMPLE_RATE            (_IMG_ERR + 0x00CE)  // Invalid pixel sampling rate
#define  IMG_ERR_BAD_SAMSUNG_VSYNC_EDGE             (_IMG_ERR + 0x00CF)  // Invalid edge for vsync to follow
#define  IMG_ERR_SAMSUNG_LUMA_GAIN_CTRL             (_IMG_ERR + 0x00D0)  // Invalid method to control the luma gain
#define  IMG_ERR_BAD_SET_COMB_COEF                  (_IMG_ERR + 0x00D1)  // Invalid way to set the chroma comb coefficients
#define  IMG_ERR_SAMSUNG_CHROMA_TRACK               (_IMG_ERR + 0x00D2)  // Invalid method to track chroma
#define  IMG_ERR_SAMSUNG_DROP_LINES                 (_IMG_ERR + 0x00D3)  // Invalid algorithm to drop video lines
#define  IMG_ERR_VHA_OPTIMIZATION_NOT_ALLOWED       (_IMG_ERR + 0x00D4)  // VHA optimization not allowed, based upon the current configuration
#define  IMG_ERR_BAD_PG_TRANSITION                  (_IMG_ERR + 0x00D5)  // A pattern generation transition is invalid
#define  IMG_ERR_TOO_MANY_PG_TRANSITIONS            (_IMG_ERR + 0x00D6)  // User is attempting to generate more pattern generation transitions than we support
#define  IMG_ERR_BAD_CL_DATA_CONFIG                 (_IMG_ERR + 0x00D7)  // Invalid data configuration for the Camera Link chips
#define  IMG_ERR_BAD_OCCURRENCE                     (_IMG_ERR + 0x00D8)  // The given occurrence is not valid.
#define  IMG_ERR_BAD_PG_MODE                        (_IMG_ERR + 0x00D9)  // Invalid pattern generation mode
#define  IMG_ERR_BAD_PG_SOURCE                      (_IMG_ERR + 0x00DA)  // Invalid pattern generation source signal
#define  IMG_ERR_BAD_PG_GATE                        (_IMG_ERR + 0x00DB)  // Invalid pattern generation gate signal
#define  IMG_ERR_BAD_PG_GATE_POLARITY               (_IMG_ERR + 0x00DC)  // Invalid pattern generation gate polarity
#define  IMG_ERR_BAD_PG_WAVEFORM_INITIAL_STATE      (_IMG_ERR + 0x00DD)  // Invalid pattern generation waveform initial state
#define  IMG_ERR_INVALID_CAMERA_ATTRIBUTE           (_IMG_ERR + 0x00DE)  // The requested camera attribute is invalid
#define  IMG_ERR_BOARD_CLOSED                       (_IMG_ERR + 0x00DF)  // The request failed because the board was closed
#define  IMG_ERR_FILE_NOT_FOUND                     (_IMG_ERR + 0x00E0)  // The requested file could not be found
#define  IMG_ERR_BAD_1409_DSP_FILE                  (_IMG_ERR + 0x00E1)  // The dspfilter1409.bin file was corrupt or missing
#define  IMG_ERR_BAD_SCARABXCV200_32_FILE           (_IMG_ERR + 0x00E2)  // The scarabXCV200.bin file was corrupt or missing
#define  IMG_ERR_BAD_SCARABXCV200_16_FILE           (_IMG_ERR + 0x00E3)  // The scarab16bit.bin file was corrupt or missing
#define  IMG_ERR_BAD_CAMERA_LINK_FILE               (_IMG_ERR + 0x00E4)  // The data1428.bin file was corrupt or missing
#define  IMG_ERR_BAD_1411_CSC_FILE                  (_IMG_ERR + 0x00E5)  // The colorspace.bin file was corrupt or missing
#define  IMG_ERR_BAD_ERROR_CODE                     (_IMG_ERR + 0x00E6)  // The error code passed into imgShowError was unknown.
#define  IMG_ERR_DRIVER_TOO_OLD                     (_IMG_ERR + 0x00E7)  // The board requires a newer version of the driver.
#define  IMG_ERR_INSTALLATION_CORRUPT               (_IMG_ERR + 0x00E8)  // A driver piece is not present (.dll, registry entry, etc).
#define  IMG_ERR_NO_ONBOARD_MEMORY                  (_IMG_ERR + 0x00E9)  // There is no onboard memory, thus an onboard acquisition cannot be performed.
#define  IMG_ERR_BAD_BAYER_PATTERN                  (_IMG_ERR + 0x00EA)  // The Bayer pattern specified is invalid.
#define  IMG_ERR_CANNOT_INITIALIZE_BOARD            (_IMG_ERR + 0x00EB)  // The board is not operating correctly and cannot be initialized.
#define  IMG_ERR_CALIBRATION_DATA_CORRUPT           (_IMG_ERR + 0x00EC)  // The stored calibration data has been corrupted.
#define  IMG_ERR_DRIVER_FAULT                       (_IMG_ERR + 0x00ED)  // The driver attempted to perform an illegal operation.
#define  IMG_ERR_ADDRESS_OUT_OF_RANGE               (_IMG_ERR + 0x00EE)  // An attempt was made to access a chip beyond it's addressable range.
#define  IMG_ERR_ONBOARD_ACQUISITION                (_IMG_ERR + 0x00EF)  // The requested operation is not valid for onboard acquisitions.
#define  IMG_ERR_NOT_AN_ONBOARD_ACQUISITION         (_IMG_ERR + 0x00F0)  // The requested operation is only valid for onboard acquisitions.
#define  IMG_ERR_BOARD_ALREADY_INITIALIZED          (_IMG_ERR + 0x00F1)  // An attempt was made to call an initialization function on a board that was already initialized.
#define  IMG_ERR_NO_SERIAL_PORT                     (_IMG_ERR + 0x00F2)  // Tried to use the serial port on a board that doesn't have one
#define  IMG_ERR_BAD_VENABLE_GATING_MODE            (_IMG_ERR + 0x00F3)  // The VENABLE gating mode selection is invalid
#define  IMG_ERR_BAD_1407_LUT_FILE                  (_IMG_ERR + 0x00F4)  // The lutfpga1407.bin was corrupt or missing
#define  IMG_ERR_BAD_SYNC_DETECT_LEVEL              (_IMG_ERR + 0x00F5)  // The detect sync level is out of range for the 1407 rev A-D
#define  IMG_ERR_BAD_1405_GAIN_FILE                 (_IMG_ERR + 0x00F6)  // The gain1405.bin file was corrupt or missing
#define  IMG_ERR_CLAMP_DAC_NOT_PRESENT              (_IMG_ERR + 0x00F7)  // The device doesn't have a clamp DAC
#define  IMG_ERR_GAIN_DAC_NOT_PRESENT               (_IMG_ERR + 0x00F8)  // The device doesn't have a gain DAC
#define  IMG_ERR_REF_DAC_NOT_PRESENT                (_IMG_ERR + 0x00F9)  // The device doesn't have a reference DAC
#define  IMG_ERR_BAD_SCARABXC2S200_FILE             (_IMG_ERR + 0x00FA)  // The scarab16bit.bin file was corrupt or missing
#define  IMG_ERR_BAD_LUT_GAIN                       (_IMG_ERR + 0x00FB)  // The desired LUT gain is invalid
#define  IMG_ERR_BAD_MAX_BUF_LIST_ITER              (_IMG_ERR + 0x00FC)  // The desired maximum number of buffer list iterations to store on onboard memory is invalid
#define  IMG_ERR_BAD_PG_LINE_NUM                    (_IMG_ERR + 0x00FD)  // The desired pattern generation line number is invalid
#define  IMG_ERR_BAD_BITS_PER_PIXEL                 (_IMG_ERR + 0x00FE)  // The desired number of bits per pixel is invalid
#define  IMG_ERR_TRIGGER_ALARM                      (_IMG_ERR + 0x00FF)  // Triggers are coming in too fast to handle them and maintain system responsiveness.  Check for glitches on your trigger line.
#define  IMG_ERR_BAD_SCARABXC2S200_03052009_FILE    (_IMG_ERR + 0x0100)  // The scarabXC2S200_03052009.bin file was corrupt or missing
#define  IMG_ERR_LUT_CONFIG                         (_IMG_ERR + 0x0101)  // There was an error configuring the LUT
#define  IMG_ERR_CONTROL_FPGA_REQUIRES_NEWER_DRIVER (_IMG_ERR + 0x0102)  // The Control FPGA requires a newer version of the driver than is currently installed.  This can happen when field upgrading the Control FPGA.
#define  IMG_ERR_CONTROL_FPGA_PROGRAMMING_FAILED    (_IMG_ERR + 0x0103) // The FlashCPLD reported that the Control FPGA did not program successfully.
#define  IMG_ERR_BAD_TRIGGER_SIGNAL_LEVEL           (_IMG_ERR + 0x0104) // A trigger signalling level is invalid.
#define  IMG_ERR_CAMERA_FILE_REQUIRES_NEWER_DRIVER  (_IMG_ERR + 0x0105) // The camera file requires a newer version of the driver
#define  IMG_ERR_DUPLICATED_BUFFER                  (_IMG_ERR + 0x0106) // The same image was put in the buffer list twice.  LabVIEW only.
#define  IMG_ERR_NO_ERROR                           (_IMG_ERR + 0x0107) // No error.  Never returned by the driver.
#define  IMG_ERR_INTERFACE_NOT_SUPPORTED            (_IMG_ERR + 0x0108) // The camera file does not support the board that is trying to open it.
#define  IMG_ERR_BAD_PCLK_POLARITY                  (_IMG_ERR + 0x0109) // The requested polarity for the pixel clock is invalid.
#define  IMG_ERR_BAD_ENABLE_POLARITY                (_IMG_ERR + 0x010A) // The requested polarity for the enable line is invalid.
#define  IMG_ERR_BAD_PCLK_SIGNAL_LEVEL              (_IMG_ERR + 0x010B) // The requested signaling level for the pixel clock is invalid.
#define  IMG_ERR_BAD_ENABLE_SIGNAL_LEVEL            (_IMG_ERR + 0x010C) // The requested signaling level for the enable line is invalid.
#define  IMG_ERR_BAD_DATA_SIGNAL_LEVEL              (_IMG_ERR + 0x010D) // The requested signaling level for the data lines is invalid.
#define  IMG_ERR_BAD_CTRL_SIGNAL_LEVEL              (_IMG_ERR + 0x010E) // The requested signaling level for the control lines is invalid.
#define  IMG_ERR_BAD_WINDOW_HANDLE                  (_IMG_ERR + 0x010F) // The given window handle is invalid
#define  IMG_ERR_CANNOT_WRITE_FILE                  (_IMG_ERR + 0x0110) // Cannot open the requested file for writing.
#define  IMG_ERR_CANNOT_READ_FILE                   (_IMG_ERR + 0x0111) // Cannot open the requested file for reading.
#define  IMG_ERR_BAD_SIGNAL_TYPE                    (_IMG_ERR + 0x0112) // The signal passed into imgSessionWaitSignal(Async) was invalid.
#define  IMG_ERR_BAD_SAMPLES_PER_LINE               (_IMG_ERR + 0x0113) // Invalid samples per line
#define  IMG_ERR_BAD_SAMPLES_PER_LINE_REF           (_IMG_ERR + 0x0114) // Invalid samples per line reference
#define  IMG_ERR_USE_EXTERNAL_HSYNC                 (_IMG_ERR + 0x0115) // The current video signal requires an external HSYNC to be used to lock the signal.
#define  IMG_ERR_BUFFER_NOT_ALIGNED                 (_IMG_ERR + 0x0116) // An image buffer is not properly aligned.  It must be aligned to a DWORD boundary.
#define  IMG_ERR_ROWPIXELS_TOO_SMALL                (_IMG_ERR + 0x0117) // The number of pixels per row is less than the region of interest width.
#define  IMG_ERR_ROWPIXELS_NOT_ALIGNED              (_IMG_ERR + 0x0118) // The number of pixels per row is not properly aligned.  The total number of bytes per row must be aligned to a DWORD boundary.
#define  IMG_ERR_ROI_WIDTH_NOT_ALIGNED              (_IMG_ERR + 0x0119) // The ROI width is not properly aligned.  The total number of bytes bounded by ROI width must be aligned to a DWORD boundary.
#define  IMG_ERR_LINESCAN_NOT_ALLOWED               (_IMG_ERR + 0x011A) // Linescan mode is not allowed for this tap configuration.
#define  IMG_ERR_INTERFACE_FILE_REQUIRES_NEWER_DRIVER (_IMG_ERR + 0x011B) // The camera file requires a newer version of the driver
#define  IMG_ERR_BAD_SKIP_COUNT                     (_IMG_ERR + 0x011C) // The requested skip count value is out of range.
#define  IMG_ERR_BAD_NUM_X_ZONES                    (_IMG_ERR + 0x011D) // The number of X-zones is invalid
#define  IMG_ERR_BAD_NUM_Y_ZONES                    (_IMG_ERR + 0x011E) // The number of Y-zones is invalid
#define  IMG_ERR_BAD_NUM_TAPS_PER_X_ZONE            (_IMG_ERR + 0x011F) // The number of taps per X-zone is invalid
#define  IMG_ERR_BAD_NUM_TAPS_PER_Y_ZONE            (_IMG_ERR + 0x0120) // The number of taps per Y-zone is invalid
#define  IMG_ERR_BAD_TEST_IMAGE_TYPE                (_IMG_ERR + 0x0121) // The requested test image type is invalid
#define  IMG_ERR_CANNOT_ACQUIRE_FROM_CAMERA         (_IMG_ERR + 0x0122) // This firmware is not capable of acquiring from a camera
#define  IMG_ERR_BAD_CTRL_LINE_SOURCE               (_IMG_ERR + 0x0123) // The selected source for one of the camera control lines is bad
#define  IMG_ERR_BAD_PIXEL_EXTRACTOR                (_IMG_ERR + 0x0124) // The desired pixel extractor is invalid
#define  IMG_ERR_BAD_NUM_TIME_SLOTS                 (_IMG_ERR + 0x0125) // The desired number of time slots is invalid
#define  IMG_ERR_BAD_PLL_VCO_DIVIDER                (_IMG_ERR + 0x0126) // The VCO divide by number was invalide for the ICS1523
#define  IMG_ERR_CRITICAL_TEMP                      (_IMG_ERR + 0x0127) // The device temperature exceeded the critical temperature threshold
#define  IMG_ERR_BAD_DPA_OFFSET                     (_IMG_ERR + 0x0128) // The requested dynamic phase aligner offset is invalid
#define  IMG_ERR_BAD_NUM_POST_TRIGGER_BUFFERS       (_IMG_ERR + 0x0129) // The requested number of post trigger buffers is invalid
#define  IMG_ERR_BAD_DVAL_MODE                      (_IMG_ERR + 0x012A) // The requested DVAL mode is invalid
#define  IMG_ERR_BAD_TRIG_GEN_REARM_SOURCE          (_IMG_ERR + 0x012B) // The requested trig gen rearm source signal is invalid
#define  IMG_ERR_BAD_ASM_GATE_SOURCE                (_IMG_ERR + 0x012C) // The requested ASM gate signal is invalid
#define  IMG_ERR_TOO_MANY_BUFFERS                   (_IMG_ERR + 0x012D) // The requested number of buffer list buffers is not supported by this IMAQ device
#define  IMG_ERR_BAD_TAP_4_VALID_RECT               (_IMG_ERR + 0x012E) // Invalid tap 4 valid rect
#define  IMG_ERR_BAD_TAP_5_VALID_RECT               (_IMG_ERR + 0x012F) // Invalid tap 5 valid rect
#define  IMG_ERR_BAD_TAP_6_VALID_RECT               (_IMG_ERR + 0x0130) // Invalid tap 6 valid rect
#define  IMG_ERR_BAD_TAP_7_VALID_RECT               (_IMG_ERR + 0x0131) // Invalid tap 7 valid rect
#define  IMG_ERR_FRONT_END_BANDWIDTH_EXCEEDED       (_IMG_ERR + 0x0132) // The camera is providing image data faster than the IMAQ device can receive it.
#define  IMG_ERR_BAD_PORT_NUMBER                    (_IMG_ERR + 0x0133) // The requested port number does not exist.
#define  IMG_ERR_PORT_CONFIG_CONFLICT               (_IMG_ERR + 0x0134) // The requested port cannot be cannot be configured due to a conflict with another port that is currently opened.
#define  IMG_ERR_BITSTREAM_INCOMPATIBLE             (_IMG_ERR + 0x0135) // The requested bitstream is not compatible with the IMAQ device.
#define  IMG_ERR_SERIAL_PORT_IN_USE                 (_IMG_ERR + 0x0136) // The requested serial port is currently in use and is not accessible.
#define  IMG_ERR_BAD_ENCODER_DIVIDE_FACTOR          (_IMG_ERR + 0x0137) // The requested encoder divide factor is invalid.
#define  IMG_ERR_ENCODER_NOT_SUPPORTED              (_IMG_ERR + 0x0138) // Encoder support is not present for this IMAQ device.  Please verify that this device is capable of handling encoder signals and that phase A and B are connected.
#define  IMG_ERR_BAD_ENCODER_POLARITY               (_IMG_ERR + 0x0139) // The requested encoder phase signal polarity is invalid.
#define  IMG_ERR_BAD_ENCODER_FILTER                 (_IMG_ERR + 0x013A) // The requested encoder filter setting is invalid.
#define  IMG_ERR_ENCODER_POSITION_NOT_SUPPORTED     (_IMG_ERR + 0x013B) // This IMAQ device does not support reading the absolute encoder position.
#define  IMG_ERR_IMAGE_IN_USE                       (_IMG_ERR + 0x013C) // The IMAQ image appears to be in use.  Please name the images differently to avoid this situation.
#define  IMG_ERR_BAD_SCARABXL4000_FILE              (_IMG_ERR + 0x013D) // The scarab.bin file is corrupt or missing
#define  IMG_ERR_BAD_CAMERA_ATTRIBUTE_VALUE         (_IMG_ERR + 0x013E) // The requested camera attribute value is invalid.  For numeric camera attributes, please ensure that the value is properly aligned and within the allowable range.
#define  IMG_ERR_BAD_PULSE_WIDTH                    (_IMG_ERR + 0x013F) // The requested pulse width is invalid.
#define  IMG_ERR_FPGA_FILE_NOT_FOUND                (_IMG_ERR + 0x0140) // The requested FPGA bitstream file could not be found.
#define  IMG_ERR_FPGA_FILE_CORRUPT                  (_IMG_ERR + 0x0141) // The requested FPGA bitstream file is corrupt.
#define  IMG_ERR_BAD_PULSE_DELAY                    (_IMG_ERR + 0x0142) // The requested pulse delay is invalid.
#define  IMG_ERR_BAD_PG_IDLE_SIGNAL_LEVEL           (_IMG_ERR + 0x0143) // On SecondGen boards tristating the idle state is all or nothing.
#define  IMG_ERR_BAD_PG_WAVEFORM_IDLE_STATE         (_IMG_ERR + 0x0144) // Invalid pattern generation waveform idle state
#define  IMG_ERR_64_BIT_MEMORY_NOT_SUPPORTED        (_IMG_ERR + 0x0145) // This device only supports acquiring into the 32-bit address space; however, portions of the image buffer list reside outside of 32-bit physical memory.
#define  IMG_ERR_64_BIT_MEMORY_UPDATE_AVAILABLE     (_IMG_ERR + 0x0146) // This 32-bit device is operating on a 64-bit OS with more than 3GB of physical memory.  An update is available to allow acquisitions into 64-bit physical memory.  Launch the updater from the menu in MAX:  Tools >> NI Vision >> NI-IMAQ Firmware Updater.
#define  IMG_ERR_32_BIT_MEMORY_LIMITATION           (_IMG_ERR + 0x0147) // This 32-bit device is operating on a 64-bit OS with more than 3GB of physical memory.  This configuration could allocate 64-bit memory which is unsupported by the device.  To solve this problem, reduce the amount of physical memory in the system.
#define  IMG_ERR_KERNEL_NOT_LOADED                  (_IMG_ERR + 0x0148) // The kernel component of the driver, niimaqk.sys, is not loaded.  Verify that an IMAQ device is in your system or reinstall the driver.
#define  IMG_ERR_BAD_SENSOR_SHUTTER_PERIOD          (_IMG_ERR + 0x0149) // The sensor shutter period is invalid.  Check the horizontal and vertical shutter period values.
#define  IMG_ERR_BAD_SENSOR_CCD_TYPE                (_IMG_ERR + 0x014A) // The sensor CCD type is invalid.
#define  IMG_ERR_BAD_SENSOR_PARTIAL_SCAN            (_IMG_ERR + 0x014B) // The sensor partial scan mode is invalid.
#define  IMG_ERR_BAD_SENSOR_BINNING                 (_IMG_ERR + 0x014C) // The sensor binning mode is invalid.
#define  IMG_ERR_BAD_SENSOR_GAIN                    (_IMG_ERR + 0x014D) // The sensor gain value is invalid.
#define  IMG_ERR_BAD_SENSOR_BRIGHTNESS              (_IMG_ERR + 0x014E) // The sensor brightness value is invalid.
#define  IMG_ERR_BAD_LED_STATE                      (_IMG_ERR + 0x014F) // The LED state is invalid.
#define  IMG_ERR_64_BIT_NOT_SUPPORTED				(_IMG_ERR + 0x0150) // The operation is not supported for 64-bit applications. 
#define  IMG_ERR_BAD_TRIGGER_DELAY                  (_IMG_ERR + 0x0151) // The requested trigger delay value is not supported
#define  IMG_ERR_LIGHTING_CURRENT_EXCEEDS_LIMITS    (_IMG_ERR + 0x0152) // The configured lighting current exceeds the hardware or user's configured limits
#define  IMG_ERR_LIGHTING_INVALID_MODE              (_IMG_ERR + 0x0153) // The configured lighting mode is invalid
#define  IMG_ERR_LIGHTING_EXTERNAL_INVALID_MODE     (_IMG_ERR + 0x0154) // The configured external lighting mode is invalid
#define  IMG_ERR_BAD_SENSOR_EXPOSURE                (_IMG_ERR + 0x0155) // The sensor exposure time is invalid.
#define  IMG_ERR_BAD_FRAME_RATE                     (_IMG_ERR + 0x0156) // The frame rate is invalid for the current configuration.
#define  IMG_ERR_BAD_SENSOR_PARTIAL_SCAN_BINNING_COMBINATION (_IMG_ERR + 0x0157) // The partial scan mode / binning mode combination is invalid.
#define  IMG_ERR_SOFTWARE_TRIGGER_NOT_CONFIGURED    (_IMG_ERR + 0x0158) // The requested software trigger is not configured.
#define  IMG_ERR_FREE_RUN_MODE_NOT_ALLOWED          (_IMG_ERR + 0x0159) // Free-run mode is not allowed in the current configuration.  This is typically caused by simultaneously enabling free-run mode and a triggered acquisition.
#define  IMG_ERR_BAD_LIGHTING_RAMPUP                (_IMG_ERR + 0x015A) // The lighting ramp-up delay is either less than the minimum value allowed or larger than the maximum time that the light is allowed to be on.
#define  IMG_ERR_AFE_CONFIG_TIMEOUT                 (_IMG_ERR + 0x015B) // Internal Error: A write to the AFEConfig register did not complete properly.
#define  IMG_ERR_LIGHTING_ARM_TIMEOUT               (_IMG_ERR + 0x015C) // Internal Error: The arming of the lighting controller did not complete properly.
#define  IMG_ERR_LIGHTING_SHORT_CIRCUIT             (_IMG_ERR + 0x015D) // A short circuit has been detected in the internal lighting current controller.  Remove the short circuit before restarting the acquisition.
#define  IMG_ERR_BAD_BOARD_HEALTH                   (_IMG_ERR + 0x015E) // The board health register has indicated an internal problem.
#define  IMG_ERR_LIGHTING_BAD_CONTINUOUS_CURRENT_LIMIT (_IMG_ERR + 0x015F) // The requested continuous current limit for the lighting controller is less than the minimum allowed current.
#define  IMG_ERR_LIGHTING_BAD_STROBE_DUTY_CYCLE_LIMIT (_IMG_ERR + 0x0160) // The requested duty cycle limit for the lighting controller strobe mode is invalid.
#define  IMG_ERR_LIGHTING_BAD_STROBE_DURATION_LIMIT (_IMG_ERR + 0x0161) // The requested duration limit for the lighting controller strobe mode is invalid.
#define  IMG_ERR_BAD_LIGHTING_CURRENT_EXPOSURE_COMBINATION (_IMG_ERR + 0x0162) // The lighting current is invalid because the exposure time plus the lighting ramp-up time exceeds either the strobe duration limit or the strobe duty cycle limit.
#define  IMG_ERR_LIGHTING_HEAD_CONFIG_NOT_FOUND     (_IMG_ERR + 0x0163) // The configuration for the desired light head was not found
#define  IMG_ERR_LIGHTING_HEAD_DATA_CORRUPT         (_IMG_ERR + 0x0164) // The data for the desired light head is invalid or corrupt.
#define  IMG_ERR_LIGHTING_ABORT_TIMEOUT             (_IMG_ERR + 0x0165) // Internal Error: The abort of the lighting controller did not complete properly.
#define  IMG_ERR_LIGHTING_BAD_STROBE_CURRENT_LIMIT  (_IMG_ERR + 0x0166) // The requested strobe current limit for the lighting controller is less than the minimum allowed current.
#define  IMG_ERR_DMA_ENGINE_UNRESPONSIVE            (_IMG_ERR + 0x0167) // Internal Error: The DMA engine is unresponsive.  Reboot the target.  If the problem persists contact National Instruments.
#define IMG_ERR_LAST_ERROR           (_IMG_ERR + 0x167)


//============================================================================
//  Functions
//============================================================================
USER_FUNC imgInterfaceOpen(const Int8* interface_name, INTERFACE_ID* ifid);
USER_FUNC imgSessionOpen(INTERFACE_ID ifid, SESSION_ID* sid);
USER_FUNC imgClose(uInt32 void_id, uInt32 freeResources);
USER_FUNC imgSnap(SESSION_ID sid, void **bufAddr);
USER_FUNC imgSnapArea(SESSION_ID sid, void **bufAddr,uInt32 top,uInt32 left, uInt32 height, uInt32 width,uInt32 rowBytes);
USER_FUNC imgGrabSetup(SESSION_ID sid, uInt32 startNow);
USER_FUNC imgGrab(SESSION_ID sid, void** bufPtr, uInt32 syncOnVB);
USER_FUNC imgGrabArea(SESSION_ID sid, void** bufPtr, uInt32 syncOnVB, uInt32 top, uInt32 left, uInt32 height, uInt32 width, uInt32 rowBytes);
USER_FUNC imgRingSetup(SESSION_ID sid,  uInt32 numberBuffer,void* bufferList[], uInt32 skipCount, uInt32 startnow);
USER_FUNC imgSequenceSetup(SESSION_ID sid,  uInt32 numberBuffer,void* bufferList[], uInt32 skipCount[], uInt32 startnow, uInt32 async);
USER_FUNC imgSessionStartAcquisition(SESSION_ID sid);
USER_FUNC imgSessionStopAcquisition(SESSION_ID sid);
USER_FUNC imgSessionStatus(SESSION_ID sid, uInt32* boardStatus, uInt32* bufIndex);
USER_FUNC imgSessionConfigureROI(SESSION_ID sid, uInt32 top, uInt32 left, uInt32 height, uInt32 width);
USER_FUNC imgSessionGetROI(SESSION_ID sid, uInt32* top, uInt32* left, uInt32* height, uInt32* width);
USER_FUNC imgSessionGetBufferSize(SESSION_ID sid, uInt32* sizeNeeded);
USER_FUNC imgGetAttribute(uInt32 void_id, uInt32 type, void* value);
USER_FUNC imgCreateBuffer(SESSION_ID sid, uInt32 where, uInt32 bufferSize, void** bufAddr);
USER_FUNC imgDisposeBuffer(void* bufferPtr);
USER_FUNC imgCreateBufList(uInt32 numElements, BUFLIST_ID* bufListId);
USER_FUNC imgDisposeBufList(BUFLIST_ID bid, uInt32 freeResources);
USER_FUNC imgGetBufferElement(BUFLIST_ID bid, uInt32 element, uInt32 itemType, void *itemValue);
USER_FUNC imgSessionConfigure(SESSION_ID sid, BUFLIST_ID buflist);
USER_FUNC imgSessionAcquire(SESSION_ID sid, uInt32 async, CALL_BACK_PTR callback);
USER_FUNC imgSessionAbort(SESSION_ID sid, uInt32* bufNum);
USER_FUNC imgSessionReleaseBuffer(SESSION_ID sid);
USER_FUNC imgSessionClearBuffer(SESSION_ID sid, uInt32 buf_num, uInt8 pixel_value);
USER_FUNC imgSessionGetLostFramesList(SESSION_ID sid, uInt32* framelist, uInt32 numEntries);
USER_FUNC imgSessionSetUserLUT8bit(SESSION_ID sid, uInt32 lutType, uInt8 *lut);
USER_FUNC imgSessionSetUserLUT16bit(SESSION_ID sid, uInt32 lutType, uInt16 *lut);
USER_FUNC imgGetCameraAttributeNumeric(SESSION_ID sid, const Int8* attributeString,double *currentValueNumeric);
USER_FUNC imgSetCameraAttributeNumeric(SESSION_ID sid, const Int8* attributeString,double newValueNumeric);
USER_FUNC imgGetCameraAttributeString(SESSION_ID sid, const Int8* attributeString,Int8* currentValueString,uInt32 sizeofCurrentValueString);
USER_FUNC imgSetCameraAttributeString(SESSION_ID sid, const Int8* attributeString,Int8* newValueString);
USER_FUNC imgSessionSerialWrite(SESSION_ID sid, Int8 *buffer, uInt32 *bufSize, uInt32 timeout);
USER_FUNC imgSessionSerialRead(SESSION_ID sid, Int8 *buffer, uInt32 *bufSize, uInt32 timeout);
USER_FUNC imgSessionSerialReadBytes(SESSION_ID sid, char* buffer, uInt32 *bufferSize, uInt32 timeout);
USER_FUNC imgSessionSerialFlush(SESSION_ID sid);
USER_FUNC imgPulseCreate2(uInt32 timeBase, uInt32 delay, uInt32 width, IMG_SIGNAL_TYPE signalType, uInt32 signalIdentifier, uInt32 signalPolarity, IMG_SIGNAL_TYPE outputType, uInt32 outputNumber, uInt32 outputPolarity, uInt32 pulseMode, PULSE_ID* plsID);
USER_FUNC imgPulseDispose(PULSE_ID plsID);
USER_FUNC imgPulseRate(double delaytime, double widthtime, uInt32* delay, uInt32* width, uInt32* timebase);
USER_FUNC imgPulseStart(PULSE_ID pid,SESSION_ID sid);
USER_FUNC imgPulseStop(PULSE_ID pid);
USER_FUNC imgSessionWaitSignal2(SESSION_ID sid, IMG_SIGNAL_TYPE signalType, uInt32 signalIdentifier, uInt32 signalPolarity, uInt32 timeout);
USER_FUNC imgSessionWaitSignalAsync2(SESSION_ID sid, IMG_SIGNAL_TYPE signalType, uInt32 signalIdentifier, uInt32 signalPolarity, CALL_BACK_PTR2 funcptr, void* callbackData);
USER_FUNC imgSessionTriggerDrive2(SESSION_ID boardid, IMG_SIGNAL_TYPE trigType, uInt32 trigNum, uInt32 polarity, uInt32 signal);
USER_FUNC imgSessionTriggerRead2(SESSION_ID sid, IMG_SIGNAL_TYPE trigType, uInt32 trigNum, uInt32 polarity, uInt32* status);
USER_FUNC imgSessionTriggerRoute2(SESSION_ID boardid, IMG_SIGNAL_TYPE srcTriggerType, uInt32 srcTriggerNumber, IMG_SIGNAL_TYPE dstTriggerType, uInt32 dstTriggerNumber);
USER_FUNC imgSessionTriggerClear(SESSION_ID sid);
USER_FUNC imgSessionTriggerConfigure2(SESSION_ID boardid, IMG_SIGNAL_TYPE trigType, uInt32 trigNum, uInt32 polarity, uInt32 timeout, uInt32 action);
USER_FUNC imgSessionSaveBufferEx(SESSION_ID sid, void *buffer,Int8* file_name);
USER_FUNC imgShowError(IMG_ERR error, Int8* text);
USER_FUNC imgInterfaceReset(INTERFACE_ID ifid);
USER_FUNC imgInterfaceQueryNames(uInt32 index, Int8* queryName);
USER_FUNC imgCalculateBayerColorLUT(double redGain, double greenGain, double blueGain, uInt32* redLUT, uInt32* greenLUT, uInt32* blueLUT, uInt32 bitDepth);
USER_FUNC imgBayerColorDecode(void* dst, const void* src, uInt32 rows, uInt32 cols, uInt32 dstRowPixels, uInt32 srcRowPixels, const uInt32* redLUT, const uInt32* greenLUT, const uInt32* blueLUT, uInt8 bayerPattern, uInt32 bitDepth, uInt32 reserved);
USER_FUNC imgSessionLineTrigSource2(SESSION_ID boardid, IMG_SIGNAL_TYPE trigType, uInt32 trigNum, uInt32 polarity, uInt32 skip);
USER_FUNC imgSessionFitROI(SESSION_ID boardid, IMG_ROI_FIT_MODE fitMode, uInt32 top, uInt32 left, uInt32 height, uInt32 width, uInt32* fittedTop, uInt32* fittedLeft, uInt32* fittedHeight, uInt32* fittedWidth);
USER_FUNC imgEncoderResetPosition(SESSION_ID boardid);
USER_FUNC imgSessionCopyBufferByNumber(SESSION_ID boardid, uInt32 bufNumber, void* userBuffer, IMG_OVERWRITE_MODE overwriteMode, uInt32* copiedNumber, uInt32* copiedIndex);
USER_FUNC imgSessionCopyAreaByNumber(SESSION_ID boardid, uInt32 bufNumber, uInt32 top, uInt32 left, uInt32 height, uInt32 width, void* userBuffer, uInt32 rowPixels, IMG_OVERWRITE_MODE overwriteMode, uInt32* copiedNumber, uInt32* copiedIndex);
USER_FUNCC imgSetAttribute2(uInt32 void_id, uInt32 type, ...);
USER_FUNCC imgSetBufferElement2(BUFLIST_ID bid, uInt32 element, uInt32 itemType, ...);
USER_FUNC imgSessionExamineBuffer2(SESSION_ID sid, uInt32 whichBuffer, uInt32 *bufferNumber, void** bufferAddr);
USER_FUNC imgPlot2(void* hwnd, void* buffer, uInt32 leftBufOffset, uInt32 topBufOffset, uInt32 xsize, uInt32 ysize, uInt32 xpos, uInt32 ypos, uInt32 flags);
USER_FUNC imgPlotDC2(void* hdc, void* buffer, uInt32 xbuffoff, uInt32 ybuffoff, uInt32 xsize, uInt32 ysize, uInt32 xscreen, uInt32 yscreen, uInt32 flags);


//============================================================================
//  Obsolete Functions
//============================================================================
USER_FUNC imgPulseCreate(uInt32 timeBase,uInt32 delay,uInt32 width,uInt32 signal_source,uInt32 signal_polar,uInt32 output,uInt32 output_polarity,uInt32 pulse_mode,PULSE_ID* plsID);
USER_FUNC imgSessionWaitSignal(SESSION_ID sid,uInt32 signal,uInt32 signal_pol,uInt32 timeout);
USER_FUNC imgSessionWaitSignalAsync(SESSION_ID sid,uInt32 signal,uInt32 signal_pol,CALL_BACK_PTR funcptr, void* callback_data);
USER_FUNC imgSessionTriggerDrive(SESSION_ID sid,uInt32 trig_num,uInt32 trig_polarity,uInt32 trig_drive);
USER_FUNC imgSessionTriggerRead(SESSION_ID sid, uInt32 trig_num, uInt32 polarity, uInt32* status);
USER_FUNC imgSessionTriggerRoute(SESSION_ID sid, uInt32 srcTrig, uInt32 dstTrig);
USER_FUNC imgSessionTriggerConfigure(SESSION_ID sid,uInt32 trig_num,uInt32 trig_polarity,uInt32 time_out,uInt32 trig_action);
USER_FUNC imgSessionLineTrigSource(SESSION_ID boardid, uInt32 trigNum, uInt32 polarity, uInt32 skip);
USER_FUNC imgSessionWait(SESSION_ID sid);
USER_FUNC imgSessionWaitAqdone(SESSION_ID sid);
USER_FUNC imgSessionWaitVblank(SESSION_ID sid);
USER_FUNC imgWaitBuffComplete(SESSION_ID sid);
USER_FUNC imgWaitFrameDone(SESSION_ID sid);
USER_FUNC imgWaitFrameStart(SESSION_ID sid);
USER_FUNC imgMemLock(BUFLIST_ID bid);
USER_FUNC imgMemUnlock(BUFLIST_ID bid);
USER_FUNC imgSessionCopyArea(SESSION_ID boardid, uInt32 bufIndex, uInt32 top, uInt32 left, uInt32 height, uInt32 width, Ptr userBuffer, uInt32 rowPixels, uInt32 waitForBufferDone);
USER_FUNC imgSessionCopyBuffer(SESSION_ID boardid, uInt32 bufIndex, uInt8* userBuffer, uInt32 waitForBufferDone);
USER_FUNC imgSetAttribute(uInt32 void_id, uInt32 type, uInt32 value);
USER_FUNC imgSetBufferElement(BUFLIST_ID bid, uInt32 element, uInt32 itemType, uInt32 itemValue);
USER_FUNC imgSessionExamineBuffer(SESSION_ID sid, uInt32 whichBuffer,uInt32 *bufferNumber,uInt32* bufferAddr);
USER_FUNC imgPlot(GUIHNDL window,void* buffer,uInt32 leftBufOffset,uInt32 topBufOffset,uInt32 xsize,uInt32 ysize,uInt32 xpos,uInt32 ypos,uInt32 flags);
USER_FUNC imgPlotDC(GUIHNDL DeviceContext,void* buffer,uInt32 xbuffoff,uInt32 ybuffoff,uInt32 xsize,uInt32 ysize,uInt32 xscreen,uInt32 yscreen,uInt32 flags); 
 

//============================================================================
//  Deprecated Functions - These will generate a MSVC warning if used
//============================================================================
#if (defined(_MSC_VER) && (_MSC_VER >= 1300))//msvc70 or above 
    #pragma deprecated(imgSetAttribute, imgSetBufferElement, imgSessionExamineBuffer, imgPlot, imgPlotDC)
#endif


//============================================================================
//  imgSessionSetROI is obsolete.  Use imgSessionConfigureROI instead.
//============================================================================
#define imgSessionSetROI imgSessionConfigureROI


//============================================================================
//  Old 1408 revision numbers
//============================================================================
#define  PCIIMAQ1408_REVA                    0x00000000
#define  PCIIMAQ1408_REVB                    0x00000001
#define  PCIIMAQ1408_REVC                    0x00000002
#define  PCIIMAQ1408_REVF                    0x00000003
#define  PCIIMAQ1408_REVX                    0x00000004


//============================================================================
//  PCI device IDs
//============================================================================
#define  IMAQ_PCI_1405                       0x70CA1093
#define  IMAQ_PXI_1405                       0x70CE1093
#define  IMAQ_PCI_1407                       0xB0411093
#define  IMAQ_PXI_1407                       0xB0511093
#define  IMAQ_PCI_1408                       0xB0011093
#define  IMAQ_PXI_1408                       0xB0111093
#define  IMAQ_PCI_1409                       0xB0B11093
#define  IMAQ_PXI_1409                       0xB0C11093
#define  IMAQ_PCI_1410                       0x71871093
#define  IMAQ_PCI_1411                       0xB0611093
#define  IMAQ_PXI_1411                       0xB0911093
#define  IMAQ_PCI_1413                       0xB0311093
#define  IMAQ_PXI_1413                       0xB0321093
#define  IMAQ_PCI_1422                       0xB0711093
#define  IMAQ_PXI_1422                       0xB0811093
#define  IMAQ_PCI_1423                       0x70281093
#define  IMAQ_PXI_1423                       0x70291093
#define  IMAQ_PCI_1424                       0xB0211093
#define  IMAQ_PXI_1424                       0xB0221093
#define  IMAQ_PCI_1426                       0x715D1093
#define  IMAQ_PCIe_1427                      0x71BF1093
#define  IMAQ_PCI_1428                       0xB0E11093
#define  IMAQ_PXI_1428                       0x707C1093
#define  IMAQ_PCIX_1429                      0x71041093
#define  IMAQ_PCIe_1429                      0x71051093
#define  IMAQ_PCIe_1430                      0x71AE1093
#define  IMAQ_17xx                           0x71EC1093


//============================================================================
//  The end(if)
//============================================================================
#endif

