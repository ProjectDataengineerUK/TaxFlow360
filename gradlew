#!/bin/sh
set -eu
APP_HOME=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
JAR="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"
if [ ! -f "$JAR" ]; then echo "ERROR: verified gradle-wrapper.jar is required; generate it from Gradle 8.12.1 and verify checksum 2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046" >&2; exit 2; fi
exec java -classpath "$JAR" org.gradle.wrapper.GradleWrapperMain "$@"
