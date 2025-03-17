import requests

# get the latest league version, so we can also get the latest item data
riotVersionsJson = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
latestVersion = riotVersionsJson[0]
itemsJson = requests.get("https://ddragon.leagueoflegends.com/cdn/" + latestVersion + "/data/en_US/item.json").json()

assetURL = "https://ddragon.leagueoflegends.com/cdn/" + latestVersion + "/img/item/"
JhinIconAssetURL = "https://ddragon.leagueoflegends.com/cdn/" + latestVersion + "/img/champion/Jhin.png"

requirements = ["Damage", "AttackSpeed", "CriticalStrike"]
# Filter for full items used in ranked that also are used on ADCs (so dmg,crit etc)
filtered_items = {
    item_id: item_data
    for item_id, item_data in itemsJson['data'].items()
    if 'tags' in item_data and requirements[0] in item_data['tags'] or requirements[1] in item_data['tags'] or requirements[2] in item_data['tags']
       if item_data['gold']['total'] > 2200 and item_data['maps']['11'] == True
}

passiveCritBonus = 0.003
passiveSpeedBonus = 0.0025

class jhin(object):
    # Class variable for reference in calculation
    runeExtraAD = 5 + 5
    AD = 133.8 + runeExtraAD

    def __init__(self):
        self.level = 18
        self.health = 2474
        self.critDMG = 175
        self.critP = 0
        self.bonusAS = 0
        self.runeExtraAD = 5 + 5
        self.AD = 133.8 + self.runeExtraAD


class item(object):
    def __init__(self):
        self.id = 0
        self.name = ''
        self.AD = 0
        self.critP = 0
        self.bonusAS = 0

def calculate_bonus_damage_percentage(critP, bonusAS):
    if int((1.44 + (critP * passiveCritBonus) + (bonusAS * passiveSpeedBonus) * 1000) % 10) == 5:
        bonusDamagePercentage = round((1.44 + (critP * passiveCritBonus) + (bonusAS * passiveSpeedBonus)) + 0.001, 2)
    else:
        bonusDamagePercentage = round((1.44 + (critP * passiveCritBonus) + (bonusAS * passiveSpeedBonus)), 2)
    return bonusDamagePercentage


original_stats = jhin()
new_stats = jhin()
best_stats = jhin()
bestItemID = ['', '', '', '', '', '']
bestItemNames = ['', '', '', '', '', '']


def findBestItem():
    bestItemDMG = [0, 0, 0, 0, 0, 0]
    i = 0
    while i < 6:
        best_damage_increase = 0
        for id, data in filtered_items.items():
            # normalize initial new_stats values
            new_stats.AD = original_stats.AD
            new_stats.critP = original_stats.critP
            new_stats.bonusAS = original_stats.bonusAS
            ###################################
            item.id = id
            item.name = data['name']
            try:
                item.AD = data['stats']['FlatPhysicalDamageMod']
            except:
                item.AD = 0
            try:
                item.critP = data['stats']['FlatCritChanceMod'] * 100
            except:
                item.critP = 0
            try:
                item.bonusAS = data['stats']['PercentAttackSpeedMod'] * 100
            except:
                item.bonusAS = 0
            new_stats.critP = new_stats.critP + item.critP
            new_stats.bonusAS = new_stats.bonusAS + item.bonusAS
            new_stats.AD = (jhin.AD + sum(bestItemDMG) - bestItemDMG[i] + item.AD) * calculate_bonus_damage_percentage(new_stats.critP, new_stats.bonusAS)

            if new_stats.AD - original_stats.AD > best_damage_increase:
                bestItemNames[i] = item.name
                best_damage_increase = new_stats.AD - original_stats.AD
                bestItemDMG[i] = item.AD
                bestItemID[i] = item.id
                # save best stats
                best_stats.AD = new_stats.AD
                best_stats.critP = new_stats.critP
                best_stats.bonusAS = new_stats.bonusAS
                ###################################################
                if bestItemNames[i] == "Infinity Edge":
                    best_stats.critDMG = best_stats.critDMG + int(data['description'][124:126])

        # update original_stats values for next item
        original_stats.AD = best_stats.AD
        original_stats.critP = best_stats.critP
        original_stats.bonusAS = best_stats.bonusAS
        ##########################################
        # deleting the item that was selected from the list and also deleting other items according to some criteria
        del filtered_items[bestItemID[i]]
        if bestItemNames[i] == "Mortal Reminder":
            del filtered_items['3036']
        if bestItemNames[i] == "Lord Dominik's Regards":
            del filtered_items['3033']
        ###########################################

        i += 1

    print("Best damage build is:", bestItemNames, "\n")
    print("With this build you will have the following stats at lvl 18:\n")
    print("Attack Damage:", best_stats.AD)
    print("Each auto attack that crits will deal:", round(best_stats.AD * best_stats.critDMG * 0.86 / 100))
    print("Crit Chance:", best_stats.critP, "%")
    print("Crit Damage:", best_stats.critDMG * 0.86, "%")
    print("Bonus Attack Speed:", best_stats.bonusAS, "%")


findBestItem()
