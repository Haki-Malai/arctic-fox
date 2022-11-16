import AsyncStorage from '@react-native-async-storage/async-storage';
import {encode as btoa} from 'base-64';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig.extra.apiUrl;


class ApiClient {
    constructor() {
        this.baseUrl = API_URL;
    }
    
    async isAuthenticated() {
        try {
            if (await AsyncStorage.getItem('accessToken')) {
                const response = await this.get('/tokens');
                return response.ok;
            } else {
                return false;
            }
        } catch(error) {
            console.log(error);
            return false;
        }
    }

    async request(options) {
        let response = await this.requestInternal(options);
        if (response.status === 401 && options.url !== '/tokens') {
            const refreshResponse = await this.put('/tokens', {
                accessToken: await AsyncStorage.getItem('accessToken'),
            });
            if (refreshResponse.ok) {
                if (refreshResponse.body.access_token) {
                    await AsyncStorage.setItem('accessToken', refreshResponse.body.access_token);
                }
                response = this.requestInternal(options);
            }
        }
        return response;
    }
      
    async requestInternal(options) {
        let query = new URLSearchParams(options.query || {}).toString();
        if (query !== '') {
            query = '?' + query;
        }

        let response;
        try {
            response = await fetch(this.baseUrl + options.url + query, {
                method: options.method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + await AsyncStorage.getItem('accessToken'),
                    ...options.headers,
                },
                body: options.body ? JSON.stringify(options.body) : null,
            });
        }
        catch (error) {
            response = {
                ok: false,
                status: 500,
                json: async () => { return {
                        status: 500,
                        message: 'The server is unresponsive',
                        description: error.toString(),
                    }; 
                }
            };
        }

        return {
            ok: response.ok,
            status: response.status,
            body: await response.json()
        };
    }

    async get(url, query, options) {
        return this.request({method: 'GET', url, query, ...options});
    }

    async post(url, body, options) {
        return this.request({method: 'POST', url, body, ...options});
    }

    async put(url, body, options) {
        return this.request({method: 'PUT', url, body, ...options});
    }

    async delete(url, options) {
        return this.request({method: 'DELETE', url, ...options});
    }

    async login(username, password) {
        const response = await this.post('/tokens', null, {
            headers: {
                Authorization:  'Basic ' + btoa(username + ":" + password),
                'Access-Control-Allow-Origin': '*',
            }
        });
        if (response.ok) {
            await AsyncStorage.setItem('accessToken', response.body.access_token);
        }
        return response;
    }

    async logout() {
        this.delete('/tokens');
        await AsyncStorage.removeItem('accessToken');
    }

}

export const apiClient = new ApiClient();