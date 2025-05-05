import { Meteor } from 'meteor/meteor';
import { HTTP } from 'meteor/http';

Meteor.methods({
  async getServerStats() {
    console.log('Fetching server stats...');
    try {
      const response = await HTTP.call('GET', 'http://localhost:4000/api/stats');
      return response.data;
    } catch (error) {
      throw new Meteor.Error('api-error', 'Failed to fetch server stats');
    }
  }
});

Meteor.startup(() => {
  console.log('Meteor server is running!');
});