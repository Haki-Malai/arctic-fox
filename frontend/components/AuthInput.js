import React from 'react';
import { View, Text } from 'react-native';
import { TextInput as PaperInput } from 'react-native-paper';
import styles from '../style';


export default function TextInput({ errorText, description, ...props }) {
  return (
    <View style={styles.inputContainer}>
      <PaperInput
        mode="outlined"
        style={styles.input}
        {...props}
        activeOutlineColor={styles.input.activeOutlineColor}
        textColor={styles.input.textColor}
        theme={{ colors: { text: styles.input.color } }}
      />
      {description && !errorText ? (
        <Text style={styles.description}>{description}</Text>
      ) : null}
      {errorText ? <Text style={styles.error}>{errorText}</Text> : null}
    </View>
  )
}