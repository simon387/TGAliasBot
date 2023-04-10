# TGAliasBot

Alias Bot for telegram groups/channels

## Dev's Setup

+ ```pip install python-telegram-bot --upgrade``` or ```pip install python-telegram-bot -U --pre```
+ ```pip install python-telegram-bot[rate-limiter]```
+ Create the ```config.properties``` file in the project's directory, and put this content:

```
[secrets]
telegram.token=XXX
telegram.group.id=-ZZZ
telegram.developer.chat.id=WWW
[application]
# log.level = info | debug | error
log.level=info
send.start.and.stop.message=false
# 1.1 | 2
http.version=1.1
```

### Setup BotFather

1. ```/setcommands```
2. ```@TGAliasBot```
3. Copy paste this:

```
alias - create/modify new alias: ie: /alias <cmd> <newcmd>
delete_alias - delete an alias: ie: /delete_alias <alias_name>
shutdown - shutdown the bot
version - show bot version
```
