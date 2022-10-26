import { Component } from "react/cjs/react.production.min";
import Button from "../components/Button";
import Background from "../components/Background";
import Header from "../components/Header";
import Logo from "../components/Logo";

export default class WelcomeScreen extends Component {
	render() {
		return (
			<Background>
			<Logo />
			<Header>Arctic Fox</Header>
			<Button
				mode="contained"
				onPress={() => this.props.navigation.navigate('LoginScreen')}
			>
				Login
			</Button>
			<Button
				mode="contained"
				onPress={() => this.props.navigation.navigate('RegisterScreen')}
			>
				Sing Up
			</Button>
			</Background>
		);
	}
}
