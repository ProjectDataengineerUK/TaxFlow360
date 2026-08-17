@echo off
setlocal
set "APP_HOME=%~dp0"
set "WRAPPER_JAR=%APP_HOME%gradle\wrapper\gradle-wrapper.jar"
if not exist "%WRAPPER_JAR%" (
  echo ERROR: verified gradle-wrapper.jar is required; expected Gradle 8.12.1 wrapper checksum 2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046 1>&2
  exit /b 2
)
java -classpath "%WRAPPER_JAR%" org.gradle.wrapper.GradleWrapperMain %*
exit /b %ERRORLEVEL%
