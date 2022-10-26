import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import Background from '../components/Background';
import Logo from '../components/Logo';
import Header from '../components/Header';
import Button from '../components/Button';
import TextInput from '../components/AuthInput';
import BackButton from '../components/BackButton';
import { apiClient } from '../client/ApiClient';
import styles from '../style';


export default class RegisterScreen extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			username: '',
			usernameError: '',
			email: '',
			emailError: '',
			password: '',
			passwordError: ''
		}
		this.setUsername = this.setUsername.bind(this);
		this.setEmail = this.setEmail.bind(this);
		this.setPassword = this.setPassword.bind(this);
	}

	setUsername = (username) => {
		this.setState({ username: username });
	}

	setEmail = (email) => {
		this.setState({ email: email });
	}

	setPassword = (password) => {
		this.setState({ password: password });
	}

	onSignUpPressed = () => {
		apiClient.post('/users', {
			username: this.state.username,
			email: this.state.email,
			password: this.state.password
		})
		.then(response => {
			if (response.ok) {
				apiClient.login(this.state.username, this.state.password)
				.then(() => this.props.navigation.navigate('DashboardScreen'))
			} else {
				if (response.body.fields) {
					if (response.body.fields.includes('username')) {
						this.setState({ usernameError: response.body.errors.username[0] });
					} else {
						this.setState({ usernameError: '' });
					}
					if (response.body.fields.includes('email')) {
						this.setState({ emailError: response.body.errors.email[0] });
					} else {
						this.setState({ emailError: '' });
					}
					if (response.body.fields.includes('password')) {
						this.setState({ passwordError: response.body.errors.password[0] });
					} else {
						this.setState({ passwordError: '' });
					}

				} else {
					this.setState({ usernameError: response.body.description, emailError: true, passwordError: true });
				}
			}
		})
	}

	render() {
		return (
		<Background>
			<BackButton goBack={this.props.navigation.goBack} />
			<Logo />
			<Header>Create Account</Header>
			<TextInput
				label="Name"
				returnKeyType="next"
				value={this.state.username}
				onChangeText={(text) => this.setUsername(text)}
				error={!!this.state.usernameError}
				errorText={this.state.usernameError}
			/>
			<TextInput
				label="Email"
				returnKeyType="next"
				value={this.state.email}
				onChangeText={(text) => this.setEmail(text)}
				error={!!this.state.emailError}
				errorText={this.state.emailError}
				autoCapitalize="none"
				autoCompleteType="email"
				textContentType="emailAddress"
				keyboardType="email-address"
			/>
			<TextInput
				label="Password"
				returnKeyType="done"
				value={this.state.password}
				onChangeText={(text) => this.setPassword(text)}
				error={!!this.state.passwordError}
				errorText={this.state.passwordError}
				secureTextEntry
			/>
			<Button
				onPress={this.onSignUpPressed}
				mode="contained"
				style={{ marginTop: 24 }}
			>
			Sign Up
			</Button>
			<View style={styles.row}>
			<Text style={styles.text}>Already have an account? </Text>
			<TouchableOpacity onPress={() => this.props.navigation.replace('LoginScreen')}>
				<Text style={styles.link}>Login</Text>
			</TouchableOpacity>
			</View>
		</Background>
		)
	}
}