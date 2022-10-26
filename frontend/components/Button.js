import React from 'react';
import { Button as PaperButton } from 'react-native-paper';
import styles from '../style';

export default function Button({ mode, style, children, ...props }){
  return (
    <PaperButton
		style={[
			styles.button,
			style,
		]}
		labelStyle={styles.buttonText}
		mode={mode}
		loading={props.loading}
		{...props}
    >
		{children}
    </PaperButton>
  );
}