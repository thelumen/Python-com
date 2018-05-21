#!/bin/bash

source_cpp="\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/audio/fft.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/audio/signal.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/common/compression.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/common/maths.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/filter/fir.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/filter/kalman.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/attitude.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/calculation.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/calibration.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/change.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/curve.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/delivery.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/feature.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/interpolation.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/motion.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/pressure.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/stationary.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/statistic.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/math/matrix.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/math/quaternion.c\
    /home/zhoulong/CodeBlocks/AIShoe/trunk/math/vector.c"

if [ "$1" == "gcc" ]
then
    if [ "$2" == "android" ]
    then
        if [ "$3" == "Queen/trunk/app" ] || [ "$3" == "HcBle/trunk/hcble" ] || [ "$3" == "BleTest/app" ]
        then
            gcc="/opt/android-ndk/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++\
                --sysroot=/opt/android-ndk/platforms/android-14/arch-arm/\
                -I/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/include/\
                -I/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi/include/\
                -I/home/zhoulong/CodeBlocks/AIShoe/trunk/\
                /home/zhoulong/IdeaProjects/$3/src/main/jniLibs/armeabi/jniAttitude.cpp\
                /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/android.c\
                $source_cpp\
                -march=armv5te -mtune=xscale -msoft-float -funswitch-loops -finline-limit=300 -O3 -s -Wl,-rpath,lib/\
                -DANDROID -DZKHC_RELEASE -DZKHC_INITIALIZE=3\
                -ffunction-sections -funwind-tables -fstack-protector -Wall -nodefaultlibs\
                -fPIC -shared -Wl,--no-undefined -z text\
                -o /home/zhoulong/IdeaProjects/$3/src/main/jniLibs/armeabi/libjniAttitude.so\
                -Wl,-soname,libjniAttitude.so\
                -L/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi/\
                -llog -lgnustl_static -lgcc -ldl -lz -lm -lc"
            eval $gcc
        else
            echo "Queen/trunk/app | HcBle/trunk/hcble | BleTest/app"
        fi
    elif [ "$2" == "python" ]
    then
        gcc="gcc -Wall -g -fPIC -DPYTHON -DZKHC_RELEASE -DZKHC_CURVE_MODEL\
            /home/zhoulong/CodeBlocks/AIShoe/trunk/gait/python.c\
            $source_cpp\
            -o /home/zhoulong/Sublime/attitude.so\
            -shared\
            -I/usr/include/python2.7/\
            -I/usr/lib/python2.7/config/\
            -I/home/zhoulong/CodeBlocks/AIShoe/trunk/\
            -I/home/zhoulong/CodeBlocks/liblinear-2.20\
            -L/home/zhoulong/CodeBlocks/liblinear-2.20\
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
                /home/zhoulong/IdeaProjects/javacpp-1.3.2.jar\
                -cp /home/zhoulong/IdeaProjects/$2/build/intermediates/classes/debug/\
                -properties android-arm\
                -Dplatform.root=/opt/android-ndk/\
                -Dplatform.compiler=/opt/android-ndk/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++\
                -Dplatform.includepath=/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/include/:/opt/android-ndk/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi/include/:/home/zhoulong/CodeBlocks/AIShoe/trunk/\
                -d /home/zhoulong/IdeaProjects/$2/src/main/jniLibs/armeabi/ $3.Attitude"
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
