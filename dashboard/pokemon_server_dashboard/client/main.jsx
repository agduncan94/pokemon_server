import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import './main.html';

Template.serverStats.onCreated(function() {
  this.serverStats = new ReactiveVar(null);

  const fetchServerStats = () => {
    Meteor.call('getServerStats', (error, result) => {
      if (!error) {
        this.serverStats.set(result);
      }
    });
  };

  fetchServerStats();
  this.interval = setInterval(fetchServerStats, 5000);
});

Template.serverStats.helpers({
  serverStats() {
    return Template.instance().serverStats.get();
  },
  jsonPrint(jsonObject) { // with Latest Javascript ECMAScript 2015+
    return JSON.stringify(jsonObject);
  },
});