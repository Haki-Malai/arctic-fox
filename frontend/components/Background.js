import React, { memo } from 'react';
import { ImageBackground, KeyboardAvoidingView } from 'react-native';
import styles from '../style';

const Background = ({ children }) => (
	<ImageBackground
		resizeMode="repeat"
		style={styles.background}
	>
		<KeyboardAvoidingView style={styles.container} behavior="padding">
			{children}
		</KeyboardAvoidingView>
	</ImageBackground>
);

export default memo(Background);