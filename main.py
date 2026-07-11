import tkinter as tk
from tkinter import messagebox
import mysql.connector

# -------- DATABASE CONNECTION --------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",   # change to your MySQL password
    database="article_platform"
)

cursor = db.cursor()

# -------- APPLICATION --------
class ArticleApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Article Sharing Platform")
        self.root.geometry("650x500")

        self.user_id = None

        self.login_screen()

# -------- CLEAR SCREEN --------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# -------- LOGIN SCREEN --------
    def login_screen(self):

        self.clear_screen()

        tk.Label(self.root,text="Login",font=("Arial",18)).pack(pady=10)

        tk.Label(self.root,text="Username").pack()
        self.username = tk.Entry(self.root)
        self.username.pack()

        tk.Label(self.root,text="Password").pack()
        self.password = tk.Entry(self.root,show="*")
        self.password.pack()

        tk.Button(self.root,text="Login",width=15,command=self.login).pack(pady=5)
        tk.Button(self.root,text="Register",width=15,command=self.register_screen).pack()

# -------- REGISTER SCREEN --------
    def register_screen(self):

        self.clear_screen()

        tk.Label(self.root,text="Register",font=("Arial",18)).pack(pady=10)

        tk.Label(self.root,text="Username").pack()
        self.reg_user = tk.Entry(self.root)
        self.reg_user.pack()

        tk.Label(self.root,text="Password").pack()
        self.reg_pass = tk.Entry(self.root,show="*")
        self.reg_pass.pack()

        tk.Button(self.root,text="Register",command=self.register).pack(pady=5)
        tk.Button(self.root,text="Back",command=self.login_screen).pack()

# -------- HOME SCREEN --------
    def home_screen(self):

        self.clear_screen()

        tk.Label(self.root,text="Articles",font=("Arial",18)).pack(pady=10)

        tk.Button(self.root,text="Add Article",width=18,command=self.add_article_screen).pack(pady=3)
        tk.Button(self.root,text="Update Article",width=18,command=self.update_article_screen).pack(pady=3)
        tk.Button(self.root,text="Delete Article",width=18,command=self.delete_article).pack(pady=3)
        tk.Button(self.root,text="Like Article",width=18,command=self.like_article).pack(pady=3)
        tk.Button(self.root,text="Comment Article",width=18,command=self.comment_screen).pack(pady=3)
        tk.Button(self.root,text="Logout",width=18,command=self.logout).pack(pady=3)

        self.articles_list = tk.Listbox(self.root,width=80)
        self.articles_list.pack(pady=10)

        self.articles_list.bind('<Double-1>',self.view_article)

        self.load_articles()

# -------- LOAD ARTICLES --------
    def load_articles(self):

        self.articles_list.delete(0,tk.END)

        cursor.execute("SELECT id,title FROM articles ORDER BY created_at DESC")

        for article in cursor.fetchall():
            self.articles_list.insert(tk.END,f"{article[0]}. {article[1]}")

# -------- ADD ARTICLE --------
    def add_article_screen(self):

        self.clear_screen()

        tk.Label(self.root,text="Add Article",font=("Arial",18)).pack(pady=10)

        tk.Label(self.root,text="Title").pack()
        self.title_entry = tk.Entry(self.root,width=50)
        self.title_entry.pack()

        tk.Label(self.root,text="Content").pack()
        self.content_text = tk.Text(self.root,width=60,height=10)
        self.content_text.pack()

        tk.Button(self.root,text="Submit",command=self.add_article).pack(pady=5)
        tk.Button(self.root,text="Back",command=self.home_screen).pack()

    def add_article(self):

        title = self.title_entry.get()
        content = self.content_text.get("1.0",tk.END)

        cursor.execute(
        "INSERT INTO articles(user_id,title,content) VALUES(%s,%s,%s)",
        (self.user_id,title,content)
        )

        db.commit()

        messagebox.showinfo("Success","Article Added")

        self.home_screen()

# -------- VIEW ARTICLE --------
    def view_article(self,event):

        try:
            selected = self.articles_list.get(self.articles_list.curselection())
        except:
            messagebox.showwarning("Warning","Select an article")
            return

        article_id = int(selected.split(".")[0])

        cursor.execute("SELECT title,content FROM articles WHERE id=%s",(article_id,))
        article = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM likes WHERE article_id=%s",(article_id,))
        likes = cursor.fetchone()[0]

        cursor.execute("""
        SELECT users.username, comments.comment
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE article_id=%s
        """,(article_id,))

        comments = cursor.fetchall()

        comment_text=""

        if comments:
            for c in comments:
                comment_text += f"{c[0]} : {c[1]}\n"
        else:
            comment_text="No comments yet."

        messagebox.showinfo(
        article[0],
        f"{article[1]}\n\nLikes: {likes}\n\nComments:\n{comment_text}"
        )

# -------- UPDATE ARTICLE --------
    def update_article_screen(self):

        try:
            selected = self.articles_list.get(self.articles_list.curselection())
        except:
            messagebox.showwarning("Warning","Select an article")
            return

        article_id = int(selected.split(".")[0])

        self.clear_screen()

        tk.Label(self.root,text="Update Article",font=("Arial",18)).pack(pady=10)

        tk.Label(self.root,text="New Title").pack()
        self.update_title = tk.Entry(self.root,width=50)
        self.update_title.pack()

        tk.Label(self.root,text="New Content").pack()
        self.update_content = tk.Text(self.root,width=60,height=10)
        self.update_content.pack()

        tk.Button(self.root,text="Update",
        command=lambda:self.update_article(article_id)).pack()

        tk.Button(self.root,text="Back",command=self.home_screen).pack()

    def update_article(self,article_id):

        title=self.update_title.get()
        content=self.update_content.get("1.0",tk.END)

        cursor.execute("""
        UPDATE articles
        SET title=%s,content=%s
        WHERE id=%s AND user_id=%s
        """,(title,content,article_id,self.user_id))

        db.commit()

        messagebox.showinfo("Success","Article Updated")

        self.home_screen()

# -------- DELETE ARTICLE --------
    def delete_article(self):

        try:
            selected=self.articles_list.get(self.articles_list.curselection())
        except:
            messagebox.showwarning("Warning","Select an article")
            return

        article_id=int(selected.split(".")[0])

        cursor.execute(
        "DELETE FROM articles WHERE id=%s AND user_id=%s",
        (article_id,self.user_id)
        )

        db.commit()

        messagebox.showinfo("Deleted","Article Deleted")

        self.load_articles()

# -------- LIKE ARTICLE --------
    def like_article(self):

        try:
            selected=self.articles_list.get(self.articles_list.curselection())
        except:
            messagebox.showwarning("Warning","Select an article")
            return

        article_id=int(selected.split(".")[0])

        try:

            cursor.execute(
            "INSERT INTO likes(user_id,article_id) VALUES(%s,%s)",
            (self.user_id,article_id)
            )

            db.commit()

            messagebox.showinfo("Liked","You liked this article")

        except:
            messagebox.showerror("Error","You already liked this article")

# -------- COMMENT --------
    def comment_screen(self):

        try:
            selected=self.articles_list.get(self.articles_list.curselection())
        except:
            messagebox.showwarning("Warning","Select an article")
            return

        self.article_id=int(selected.split(".")[0])

        self.clear_screen()

        tk.Label(self.root,text="Add Comment",font=("Arial",18)).pack(pady=10)

        self.comment_box=tk.Text(self.root,width=60,height=6)
        self.comment_box.pack()

        tk.Button(self.root,text="Submit",command=self.add_comment).pack(pady=5)
        tk.Button(self.root,text="Back",command=self.home_screen).pack()

    def add_comment(self):

        comment=self.comment_box.get("1.0",tk.END)

        cursor.execute(
        "INSERT INTO comments(user_id,article_id,comment) VALUES(%s,%s,%s)",
        (self.user_id,self.article_id,comment)
        )

        db.commit()

        messagebox.showinfo("Success","Comment Added")

        self.home_screen()

# -------- LOGIN --------
    def login(self):

        username=self.username.get()
        password=self.password.get()

        cursor.execute(
        "SELECT id FROM users WHERE username=%s AND password=%s",
        (username,password)
        )

        user=cursor.fetchone()

        if user:
            self.user_id=user[0]
            self.home_screen()
        else:
            messagebox.showerror("Error","Invalid Login")

# -------- REGISTER --------
    def register(self):

        username=self.reg_user.get()
        password=self.reg_pass.get()

        try:

            cursor.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username,password)
            )

            db.commit()

            messagebox.showinfo("Success","Registered Successfully")

            self.login_screen()

        except:
            messagebox.showerror("Error","Username already exists")

# -------- LOGOUT --------
    def logout(self):

        self.user_id=None
        self.login_screen()

# -------- RUN PROGRAM --------
root=tk.Tk()

app=ArticleApp(root)

root.mainloop()