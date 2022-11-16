import { useEffect, useState } from 'react';
import 'react-native-gesture-handler';
import { NavigationContainer } from '@react-navigation/native';
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
        const customHeader = { title: 'Arctic Fox' };
        return (
            <SafeAreaProvider>
                <NavigationContainer>
                    <Stack.Navigator initialRouteName={navigationStart} screenOptions={{headerShown:false}} >
                        <Stack.Screen name='WelcomeScreen' component={WelcomeScreen} options={customHeader}/>
                        <Stack.Screen name='LoginScreen' component={LoginScreen} options={customHeader}/>
                        <Stack.Screen name='RegisterScreen' component={RegisterScreen} options={customHeader}/>
                        <Stack.Screen name='ResetPasswordScreen' component={ResetPasswordScreen} options={customHeader}/>
                        <Stack.Screen name='DashboardScreen' component={DashboardScreen} options={customHeader}/>
                    </Stack.Navigator>
                </NavigationContainer>
            </SafeAreaProvider>
        )
    }
}