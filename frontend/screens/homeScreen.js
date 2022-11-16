import React from 'react';
import { Text } from 'react-native-paper';
import Background from '../components/Background';
import { Image } from 'react-native';
import Header from '../components/Header';
import Button from '../components/Button';
import Logo from '../components/Logo';
import { apiClient } from '../client/ApiClient';
import styles from '../style';
import { BackHandler } from 'react-native';

export default class HomeScreen extends React.Component {
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

		return (
			<Background>
				{image}
				<Header>Hello {this.state.userData.username}!</Header>
				<Text style={styles.text}>
					You are now logged in and the session tokens are saved for next time! This is your unique gravatar!
				</Text>
			</Background>
		)
	}
}