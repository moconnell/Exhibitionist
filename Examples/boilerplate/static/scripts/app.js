/* jshint bitwise:true, newcap:true, noarg:true, noempty:true, curly:true, eqeqeq:true*/
/* jshint  forin:true, immed:true, latedef:true, nonew:true, undef:true, strict:true*/
/* jshint  indent:4, browser:true, undef: true, unused: true*/
/* global $, _, console,WebSocket */

var app = (function ($, _) { // run after document load
    "use strict";
    app = this;

    var defaults = {
        ws_url: null,
        objid: null,
        api_url: null
    };

    var settings = {};
    var ws = null;

    // private
    var onError =function (req, status, errThrown) {
        console.log("alas, 'tis a shame!");
        console.log(req, status, errThrown);
    };

    var onData = function (data) {
        // when data is recieved , put it in the "#container" div
        console.log("Got JSON data: " + data.payload);
        $("#container").html(data.payload);
    };

     // callback for incoming data on websocket
    var onWSMessage = function  (msg) {
        console.log("websocket Message received: " + msg.data);
        var d = JSON.parse(msg.data);

    };

    // callback for successfully opening websocket
    var onWSOpen = function  () {
        console.log("websocket Opened.");
        // subscribe to channel named objid
        console.log("Sending Subscribe request to channel: " + settings.objid);
        ws.send(JSON.stringify({msg_type: "SUB", channel: settings.objid}));
    };

    var openWS = function  (ws_url) {
        console.log("opening websocket to " + ws_url);

        ws = new WebSocket(ws_url);
        ws.onopen = onWSOpen;
        ws.onmessage = onWSMessage;
    };

    // public API, available from global namespace under app
    var start = function (options) {
        // override defaults with provided options
        settings = $.extend({}, defaults, options);

        openWS(settings.ws_url, settings.objid);

        // fetch json data via AJAX
        $.getJSON(settings.api_url).done(onData).error(onError);
    };

    // return our API
    return {
        start: start,
        settings: settings
    };
})($, _);

