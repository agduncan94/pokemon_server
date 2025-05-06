import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import './main.html';

Template.serverStats.onCreated(function() {
  this.serverStats = new ReactiveVar(null);
  this.currentUser = new ReactiveVar(null);

  const fetchServerStats = () => {
    Meteor.call('getServerStats', (error, result) => {
      if (!error) {
        this.serverStats.set(result);
        const randomIndex = Math.floor(Math.random() * result.users.length);

        this.currentUser.set(result.users[randomIndex])
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
  currentUser() {
    return Template.instance().currentUser.get();
  },
  jsonPrint(jsonObject) { // with Latest Javascript ECMAScript 2015+
    return JSON.stringify(jsonObject);
  },
  getCpuClass(cpuUsage) {
    const percentage = parseInt(cpuUsage, 10); // Convert to integer
    return `progress-bar p${percentage}`; // Creates class like "p40"
  },
  getPokemonServer(name) {
    return './images/pokemon_servers/' + name + '.png'
  },
  getPokemonUser(name) {
    return './images/pokemon_users/' + name + '.png'
  }


});