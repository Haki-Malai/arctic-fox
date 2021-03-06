import React from "react";
import { View, ScrollView, Text, Image, Pressable } from "react-native";
import Navigator from "./navigator.component";
import Lang from "../lang.component";
import Options from "./account/options.component";
import Avatar from "./account/avatar.component";
import styles from "../../style";

export default class Account extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            option: "none",
            remainingTasks:
                this.props.level[this.props.userData.level - 1][1] -
                this.props.userData.tasks.length,
            todayTasks: this.props.userData.tasks.length,
        };
    }
    componentDidMount() {
        this.props.refreshUserData();
    }
    render() {
        return (
            <View style={styles.container}>
                <ScrollView
                    contentContainerStyle={styles.accountScroll}
                    horizontal={false}
                    scrollEnabled={false}
                >
                    <View style={styles.account}>
                        <View style={styles.accountDetailsWrapper}>
                            <Avatar
                                avatar={this.props.avatar}
                                url={this.props.url}
                            ></Avatar>
                            <Text style={styles.accountUsername}>
                                {this.props.userData.username}
                            </Text>
                            <Text style={styles.accountDetail}>
                                {this.props.lang === "en"
                                    ? "Email:"
                                    : "Ηλεκτρονική διεύθυνση:"}
                                {this.props.userData.email}
                            </Text>
                            <Text style={styles.accountDetail}>
                                {this.props.lang === "en"
                                    ? "Level:"
                                    : "Επίπεδο:"}{" "}
                                {this.props.userData.level}
                            </Text>
                            <Text style={styles.accountDetail}>
                                {this.props.lang === "en"
                                    ? "Credit score:"
                                    : "Σκορ πίστης:"}{" "}
                                {this.props.userData.level * 600}
                            </Text>
                            <Text style={styles.accountDetail}>
                                {this.props.lang === "en"
                                    ? "Invitation Code:"
                                    : "Κωδικός πρόσκλησης:"}{" "}
                                {this.props.userData.invitationCode}
                                <Pressable
                                    style={styles.accountPressable}
                                    onPress={() =>
                                        navigator.clipboard.writeText(
                                            this.props.userData.invitationCode
                                        )
                                    }
                                >
                                    <Text style={{ color: "white" }}>
                                        {this.props.lang === "en"
                                            ? "Copy"
                                            : "Αντιγραφή"}
                                    </Text>
                                </Pressable>
                            </Text>
                        </View>
                        <Lang setLang={this.props.setLang}></Lang>
                        <View style={styles.accountTables}>
                            <View style={styles.accountTable}>
                                <Text style={styles.accountTableItem}>
                                    {this.props.userData.balance.toFixed(2)}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Balance"
                                            : "Υπόλοιπο"}
                                    </Text>
                                </Text>
                                <Text style={styles.accountTableItem}>
                                    {this.props.userData.taskProfit.toFixed(2)}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Task Profit"
                                            : "Κέρδη εργασιών"}
                                    </Text>
                                </Text>
                                <Text style={styles.accountTableItem}>
                                    {this.props.userData.invitationCommission.toFixed(
                                        2
                                    )}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Invitation Commission"
                                            : "Κέρδη προσκλήσεων"}
                                    </Text>
                                </Text>
                            </View>
                            <View style={styles.accountTable}>
                                <Text style={styles.accountTableItem}>
                                    {(
                                        this.props.userData.taskProfit +
                                        this.props.userData.invitationCommission
                                    ).toFixed(2)}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Total Profit"
                                            : "Ολικά κέρδη"}
                                    </Text>
                                </Text>
                                <Text style={styles.accountTableItem}>
                                    {this.state.todayTasks}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Today Complete"
                                            : "Σημερινές εργασίες"}
                                    </Text>
                                </Text>
                                <Text style={styles.accountTableItem}>
                                    {this.state.remainingTasks}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Today remaining"
                                            : "Σημερινές απομένουν"}
                                    </Text>
                                </Text>
                            </View>
                            <View style={styles.accountTable}>
                                <Text style={styles.accountTableItem}>
                                    {this.props.userData.balance.toFixed(2)}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? 'Today"s profit'
                                            : "Σημερινά κέρδη"}
                                    </Text>
                                </Text>
                                <Text style={styles.accountTableItem}>
                                    {this.props.userData.balance.toFixed(2)}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Weekly profit"
                                            : "Εβδομαδιαία κέρδη"}
                                    </Text>
                                </Text>
                                <Text style={styles.accountTableItem}>
                                    {this.props.userData.balance.toFixed(2)}
                                    <Text style={styles.accountTableItemLabel}>
                                        {this.props.lang === "en"
                                            ? "Monthly profit"
                                            : "Μηνιαία κέρδη"}
                                    </Text>
                                </Text>
                            </View>
                        </View>
                        <Options
                            refreshUserData={this.props.refreshUserData}
                            url={this.props.url}
                            userData={this.props.userData}
                            lang={this.props.lang}
                            logout={() => this.props.logout()}
                        ></Options>
                    </View>
                </ScrollView>
                <Navigator
                    lang={this.props.lang}
                    setPage={this.props.setPage}
                    page={3}
                />
            </View>
        );
    }
}
