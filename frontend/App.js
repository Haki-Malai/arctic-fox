import { useEffect, useState } from 'react';
import 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { createStackNavigator } from '@react-navigation/stack';
import { useLoadedAssets } from './hooks/useLoadedAssets';
import {WelcomeScreen,
    LoginScreen,
    RegisterScreen,
    ResetPasswordScreen,
    DashboardScreen} from './screens';
import { apiClient } from './client/ApiClient';


export default function App() {
    const isLoadingComplete = useLoadedAssets();
    const Stack = createStackNavigator();
    const [navigationStart, setNavigationStart] = useState('WelcomeScreen');

    useEffect(() => {
        apiClient.isAuthenticated() === true? setNavigationStart('DashboardScreen') : null;
    });

    if (!isLoadingComplete) {
        return null;
    } else {
        return (
            <SafeAreaProvider>
                <NavigationContainer>
                    <Stack.Navigator initialRouteName={navigationStart} >
                        <Stack.Screen name='WelcomeScreen' component={WelcomeScreen} />
                        <Stack.Screen name='LoginScreen' component={LoginScreen} />
                        <Stack.Screen name='RegisterScreen' component={RegisterScreen} />
                        <Stack.Screen name='ResetPasswordScreen' component={ResetPasswordScreen} />
                        <Stack.Screen name='DashboardScreen' component={DashboardScreen} />
                    </Stack.Navigator>
                </NavigationContainer>
            </SafeAreaProvider>
        )
    }
}