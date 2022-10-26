import { Component } from 'react';
import { TouchableOpacity, View, Text } from 'react-native';
import Background from '../components/Background';
import Logo from '../components/Logo';
import LoginHeader from '../components/Header';
import Button from '../components/Button';
import BackButton from '../components/BackButton';
import TextInput from '../components/AuthInput';
import { apiClient } from '../client/ApiClient';
import styles from '../style';


export default class LoginScreen extends Component {
constructor(props) {
	super(props);
	this.state = {
		username: '',
		error: '',
		password: '',
		loading: false
	}
	this.setUsername = this.setUsername.bind(this);
	this.setPassword = this.setPassword.bind(this);
	}

	setUsername = (username) => {
		this.setState({ username: username });
	}

	setPassword = (password) => {
		this.setState({ password: password });
	}

	onLoginPressed = () => {
		this.setState({ error: '', loading: true });
		apiClient.login(this.state.username, this.state.password)
		.then(response => {
			if (response.ok) {
				this.props.navigation.navigate('DashboardScreen');
			} else {
				this.setState({ error : response.body.description});
			}
			this.setState({ loading: false });
		})
	}

	render() {
		return (
		<Background>
			<BackButton goBack={this.props.navigation.goBack} />
			<Logo />
			<LoginHeader>Welcome back</LoginHeader>
			<TextInput
				label="Username"
				returnKeyType="next"
				value={this.state.username}
				onChangeText={(text) => this.setUsername(text)}
				autoCapitalize="none"
				error={!!this.state.error}
				errorText={this.state.error}
			/>
			<TextInput
				label="Password"
				returnKeyType="done"
				value={this.state.password}
				onChangeText={(text) => this.setPassword(text)}
				error={!!this.state.error}
				secureTextEntry
			/>
			<View style={styles.forgotPassword}>
			<TouchableOpacity
				onPress={() => this.props.navigation.navigate('ResetPasswordScreen')}
			>
				<Text style={styles.forgot}>Forgot your password?</Text>
			</TouchableOpacity>
			</View>
			<Button 
				mode="contained"
				onPress={this.onLoginPressed}
				loading={this.state.loading}
			>
				Login
			</Button>
			<View style={styles.row}>
			<Text style={styles.text}>Don’t have an account?</Text>
			<TouchableOpacity onPress={() => this.props.navigation.replace('RegisterScreen')}>
				<Text style={styles.link}>Sign up</Text>
			</TouchableOpacity>
			</View>
		</Background>
		)
	}
}