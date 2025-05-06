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
  this.interval = setInterval(fetchServerStats, 20000);
});

Template.serverStats.helpers({
  serverStats() {
    return Template.instance().serverStats.get();
  },
  jsonPrint(jsonObject) { // with Latest Javascript ECMAScript 2015+
    return JSON.stringify(jsonObject);
  },
  getCpuClass(cpuUsage) {
    const percentage = parseInt(cpuUsage, 10); // Convert to integer
    return `progress-bar p${percentage}`; // Creates class like "p40"
  }


});