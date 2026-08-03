import React, { useRef } from 'react';
import { StyleSheet, SafeAreaView, StatusBar, Alert } from 'react-native';
import { WebView } from 'react-native-webview';
import * as FileSystem from 'expo-file-system/legacy';

export default function App() {
  const webViewRef = useRef(null);

  const onMessage = async (event) => {
    try {
      const message = JSON.parse(event.nativeEvent.data);
      
      if (message.type === 'download_db') {
        const { href } = message;
        const localDbUri = `${FileSystem.documentDirectory}sprint_backup_active.db`;
        
        // 1. Download database natively (completely bypasses browser CORS!)
        const downloadResult = await FileSystem.downloadAsync(href, localDbUri);
        
        // 2. Read file content as base64 string
        const base64Str = await FileSystem.readAsStringAsync(downloadResult.uri, {
          encoding: FileSystem.EncodingType.Base64,
        });
        
        // 3. Inject base64 data back into Webview to load SQL.js WASM safely!
        const jsCode = `window.loadDatabaseFromBase64("${base64Str}"); true;`;
        if (webViewRef.current) {
          webViewRef.current.injectJavaScript(jsCode);
        }
      }
    } catch (err) {
      console.error("Native Bridge Error:", err);
      const jsCode = `window.hideLoadingOverlay(); alert("Ошибка моста: ${err.message}"); true;`;
      if (webViewRef.current) {
        webViewRef.current.injectJavaScript(jsCode);
      }
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F0F2F5" />
      <WebView 
        ref={webViewRef}
        source={{ uri: 'https://shamilbidjev.github.io/Sprint_program_education/mobile_app/index.html' }} 
        originWhitelist={['*']}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        onMessage={onMessage}
        style={styles.webview}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F0F2F5',
  },
  webview: {
    flex: 1,
  }
});
