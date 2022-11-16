import React from 'react';
import { Text } from 'react-native-paper';
import Background from '../components/Background';
import { Image } from 'react-native';
import Header from '../components/Header';
import Logo from '../components/Logo';
import { apiClient } from '../client/ApiClient';
import styles from '../style';
import { BackHandler } from 'react-native';

export default class SettingsScreen extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			userData: ''
		}
	}

	render() {
		var image = <Logo />
		if (this.state.userData.avatar) {
			var image = <Image source={{uri:this.state.userData.avatar}} style={styles.image}></Image>
		}

		return (
			<Background>
				{image}
				<Header>Settings</Header>
			</Background>
		)
	}
}