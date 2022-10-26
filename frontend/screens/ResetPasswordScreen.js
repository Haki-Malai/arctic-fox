import { Component } from 'react';
import Background from '../components/Background';
import BackButton from '../components/BackButton';
import Logo from '../components/Logo';
import Header from '../components/Header';
import TextInput from '../components/AuthInput';
import Button from '../components/Button';
import { apiClient } from '../client/ApiClient';

export default class ResetPasswordScreen extends Component {
  constructor(props) {
    super(props);
    this.state = {
      email: ''
    }
    this.setEmail = this.setEmail.bind(this);
  }

  setEmail = (email) => {
    this.setState({ email });
  }

  sendResetPasswordEmail = () => {
    apiClient.post('/tokens/reset', { email: this.state.email })
    .then(this.props.navigation.navigate('WelcomeScreen'))
  }

  render() {
    return (
      <Background>
        <BackButton goBack={this.props.navigation.goBack} />
        <Logo />
        <Header>Restore Password</Header>
        <TextInput
          label="E-mail address"
          returnKeyType="done"
          value={this.state.email}
          onChangeText={(text) => this.setEmail(text)}
          autoCapitalize="none"
          autoCompleteType="email"
          textContentType="emailAddress"
          keyboardType="email-address"
          description="You will receive email with password reset link."
        />
        <Button
          mode="contained"
          onPress={this.sendResetPasswordEmail}
          style={{ marginTop: 16 }}
        >
          Send Reset Link
        </Button>
      </Background>
    )
  }
}