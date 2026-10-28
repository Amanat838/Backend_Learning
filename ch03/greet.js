const users = [{ name: "Ayesha" }, { name: "Bilal" }];
function shout(user) {
  return user.name.toUpperCase();
}
function shoutAll(list) {
  return list.map((u, i) => shout(list[i]));
}
console.log(shoutAll(users));
