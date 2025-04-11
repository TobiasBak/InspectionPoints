import * as monaco from 'monaco-editor';

/**
 * DBML example
 *
 * @source https://dbml.dbdiagram.io/docs/
 */
const code = `// Use DBML to define your database structure

Table follows {
  following_user_id integer
  followed_user_id integer
  created_at timestamp 
}

Table users {
  id integer [primary key]
  username varchar
  role varchar
  created_at timestamp
}

Table posts {
  id integer [primary key]
  title varchar
  body text [note: 'Content of the post']
  user_id integer
  status varchar
  created_at timestamp
}

Ref: posts.user_id > users.id // many-to-one

Ref: users.id < follows.following_user_id

Ref: users.id < follows.followed_user_id
`;

const editorElement = document.getElementById('editor');

const editor = monaco.editor.create(editorElement!, {
    value: code,
    language: 'python',
    theme: 'vs-dark',
    minimap: {
        enabled: false,
    },
});

console.log("EDDITOTOOEORORO")
