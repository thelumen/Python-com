#!/bin/bash

source_cpp="\
    /home/longzhou/VSCode/AIShoe/trunk/audio/adpcm.c\
    /home/longzhou/VSCode/AIShoe/trunk/audio/fft.c\
    /home/longzhou/VSCode/AIShoe/trunk/audio/signal.c\
    /home/longzhou/VSCode/AIShoe/trunk/common/compression.c\
    /home/longzhou/VSCode/AIShoe/trunk/common/maths.c\
    /home/longzhou/VSCode/AIShoe/trunk/filter/fir.c\
    /home/longzhou/VSCode/AIShoe/trunk/filter/kalman.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/attitude.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/calculation.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/calibration.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/contact.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/couple.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/delivery.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/feature.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/interpolation.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/motion.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/phase.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/pressure.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/rotation.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/stationary.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/statistic.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/trend.c\
    /home/longzhou/VSCode/AIShoe/trunk/gait/zero.c\
    /home/longzhou/VSCode/AIShoe/trunk/math/matrix.c\
    /home/longzhou/VSCode/AIShoe/trunk/math/quaternion.c\
    /home/longzhou/VSCode/AIShoe/trunk/math/vector.c"

if [ "$1" == "gcc" ]
then
    if [ "$2" == "android" ]
    then
        if [ "$3" == "Queen/trunk/app" ] || [ "$3" == "HcBle/trunk/hcble" ] || [ "$3" == "BleTest/app" ]
        then
            # extern "C"
            gcc="/opt/android-toolchain/gnustl/bin/clang++\
                -I/home/longzhou/VSCode/AIShoe/trunk/\
                -x c++ /home/longzhou/IdeaProjects/$3/src/main/jniLibs/armeabi/jniAttitude.cpp\
                -x c /home/longzhou/VSCode/AIShoe/trunk/gait/android.c\
                $source_cpp\
                -mtune=xscale -msoft-float -O3 -s -Wl,-rpath,lib/\
                -DANDROID -DZKHC_RELEASE -DZKHC_INITIALIZE=3 -DZKHC_BLE\
                -ffunction-sections -funwind-tables -fstack-protector -Wall -nodefaultlibs\
                -fPIC -shared -Wl,--no-undefined -z text\
                -o /home/longzhou/IdeaProjects/$3/src/main/jniLibs/armeabi/libjniAttitude.so\
                -Wl,-soname,libjniAttitude.so\
                -llog -lstdc++ -lgcc -ldl -lz -lm -lc"
            eval $gcc
        else
            echo "Queen/trunk/app | HcBle/trunk/hcble | BleTest/app"
        fi
    elif [ "$2" == "python" ]
    then
        gcc="gcc -Wall -g -fPIC -DPYTHON -DZKHC_RELEASE\
            /home/longzhou/VSCode/AIShoe/trunk/gait/python.c\
            $source_cpp\
            -o /home/longzhou/Sublime/attitude.so\
            -shared\
            -I/usr/include/python2.7/\
            -I/usr/lib/python2.7/config/\
            -I/home/longzhou/VSCode/AIShoe/trunk/\
            -I/home/longzhou/VSCode/liblinear-2.20\
            -L/home/longzhou/VSCode/liblinear-2.20\
            -llinear"
        eval $gcc
    else
        echo "android | python"
    fi
elif [ "$1" == "jar" ]
then
    if [ "$2" == "Queen/trunk/app" ] || [ "$2" == "HcBle/trunk/hcble" ] || [ "$2" == "BleTest/app" ]
    then
        if [ "$3" == "com.zkhc.master.attitude" ] || [ "$3" == "com.zkhc.hcble" ] || [ "$3" == "com.zkhc.bletest" ]
        then
            jar="/opt/jdk1.8.0_131/bin/java -jar\
                /home/longzhou/IdeaProjects/javacpp-1.3.2.jar\
                -cp /home/longzhou/IdeaProjects/$2/build/intermediates/classes/debug/\
                -properties android-arm\
                -Dplatform.root=/opt/android-ndk/\
                -Dplatform.compiler=/opt/android-ndk/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++\
                -Dplatform.includepath=/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/include/:/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi/include/:/home/longzhou/VSCode/AIShoe/trunk/\
                -d /home/longzhou/IdeaProjects/$2/src/main/jniLibs/armeabi/ $3.Attitude"
            eval $jar
        else
            echo "com.zkhc.master.attitude | com.zkhc.hcble | com.zkhc.bletest"
        fi
    else
        echo "Queen/trunk/app | HcBle/trunk/hcble | BleTest/app"
    fi
else
    echo "gcc | jar"
fi
