import React from 'react';
import { Image } from 'react-native';
import Logo from '../components/Logo';
import { apiClient } from '../client/ApiClient';
import styles from '../style';
import { BackHandler } from 'react-native';
import HomeScreen from './homeScreen';
import ProfileScreen from './profileScreen';
import SettingsScreen from './settingsScreen';
import { createMaterialBottomTabNavigator } from '@react-navigation/material-bottom-tabs';
import style from '../style';


export default class DashboardScreen extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			userData: '',
		}
		this.handleBackButtonClick = this.handleBackButtonClick.bind(this);
	}

	handleBackButtonClick() {
		this.logout();
		return true;
	}

	logout() {
		apiClient.logout()
		.then(() => {
			this.props.navigation.reset({
			index: 0,
			routes: [{ name: 'WelcomeScreen' }],
			})
		})
	}

	componentWillMount() {
		BackHandler.addEventListener('hardwareBackPress', this.handleBackButtonClick);
	}

	componentDidMount() {
		apiClient.get('/users/me').then((response) => {
			if (response.ok) {
				this.setState({userData: response.body});
			} else if (response.status === 401) {
				this.props.navigation.reset({
					index: 0,
					routes: [{name: 'WelcomeScreen'}],
				})
			}
		});
	}

	render() {
		var image = <Logo />
		if (this.state.userData.avatar) {
			var image = <Image source={{uri:this.state.userData.avatar}} style={styles.image}></Image>
		}

		const Tab = createMaterialBottomTabNavigator();

		return (
			<Tab.Navigator barStyle={styles.bar} style={styles.barContainer} screenOptions={{headerShown:false}} >
				<Tab.Screen name='HomeScreen' component={HomeScreen} />
				<Tab.Screen name='SettingsScreen' component={SettingsScreen} />
				<Tab.Screen name='ProfileScreen' component={ProfileScreen} />
			</Tab.Navigator>
		)
	}
}