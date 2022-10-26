import React from 'react';
import { Image } from 'react-native';
import styles from '../style';

export default function Logo() {
  return <Image source={require('../assets/images/logo.png')} style={styles.image} />
}