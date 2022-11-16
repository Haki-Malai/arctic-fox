import { StyleSheet } from 'react-native';

const BLACK = "#222e36";
const BLUE = "#445C6D";
const FADED_BLUE = "#879EB0";
const SUPER_FADED_BLUE = "#CEE9EA";
const RED = "#CC241D";

export default StyleSheet.create({
	forgotPassword: {
		width: '100%',
		alignItems: 'center',
		marginBottom: 24,
		color: FADED_BLUE
	},
	row: {
		flexDirection: 'row',
		marginTop: 4,
	},
	forgot: {
		fontSize: 13,
		color: FADED_BLUE,
		flexDirection: 'row'
	},
	link: {
		fontWeight: 'bold',
		color: BLACK,
	},
	text: {
		color: BLACK,
	},
	button: {
		width: '100%',
		marginVertical: 10,
		backgroundColor: BLUE,
	},
	buttonText: {
		fontWeight: 'bold',
		fontSize: 15,
		lineHeight: 26,
		color: SUPER_FADED_BLUE
	},
	title: {
		fontSize: 20,
		fontWeight: "bold",
	},
	separator: {
		marginVertical: 30,
		height: 1,
		width: "80%",
	},
	background: {
		flex: 1,
		width: '100%',
		backgroundColor: SUPER_FADED_BLUE
	},
	container: {
		flex: 1,
		padding: 20,
		width: '100%',
		maxWidth: 340,
		alignSelf: 'center',
		alignItems: 'center',
		justifyContent: 'center',
	},
	inputContainer: {
		width: '100%',
		marginVertical: 12,
	},
	input: {
		backgroundColor: SUPER_FADED_BLUE,
        activeOutlineColor: BLUE,
		color: BLACK,
	},
	description: {
		fontSize: 13,
		paddingTop: 8,
	},
	error: {
		fontSize: 13,
		color: RED,
		paddingTop: 8,
	},
	header: {
		fontSize: 21,
		color: BLUE,
		fontWeight: 'bold',
		paddingVertical: 12,
	},
	image: {
		width: 100,
		height: 100,
		borderRadius: 50,
	},
	bar: {
		maxWidth: 400,
		width: '100%',
		alignSelf: 'center',
		backgroundColor: BLUE
	},
	barContainer: {
		backgroundColor: SUPER_FADED_BLUE,
	}
})